/**
 * SceneSpeak Client Controller (PWA)
 * 
 * Implements Section 7, 10, 12 of the SceneSpeak PDR:
 * - Camera access & auto-capture (rear facing)
 * - Canvas frame downscaling to <= 768px JPEG 0.7
 * - Client-side blur check (Laplacian variance) & brightness check (mean luminance)
 * - Immediate haptic vibration and "Looking" audio feedback
 * - Auto-speak via Web Speech API (speechSynthesis)
 * - Hazard alert audio tone & tactile vibration
 * - Voice question transcription for Ask mode (SpeechRecognition)
 * - User feedback submission (1-5 star ratings)
 */

(function () {
  "use strict";

  // --- DOM Elements ---
  const video = document.getElementById("camera-stream");
  const canvas = document.getElementById("capture-canvas");
  const cameraStatus = document.getElementById("camera-status");
  const statusOutput = document.getElementById("status-output");
  const btnDescribe = document.getElementById("btn-describe");
  const btnRead = document.getElementById("btn-read");
  const btnAsk = document.getElementById("btn-ask");
  const btnRepeat = document.getElementById("btn-repeat");
  const feedbackRow = document.getElementById("feedback-row");
  const btnFeedbackGood = document.getElementById("btn-feedback-good");
  const btnFeedbackBad = document.getElementById("btn-feedback-bad");
  const speechRateSlider = document.getElementById("speech-rate");
  const rateValueLabel = document.getElementById("rate-value");
  const btnLangToggle = document.getElementById("btn-lang-toggle");

  // --- App State ---
  let currentStream = null;
  let isProcessing = false;
  let lastSpokenText = "";
  let lastRequestId = null;
  let audioContext = null;

  // Language state (en / hi)
  let currentLang = localStorage.getItem("scenespeak_lang") || "en";
  if (btnLangToggle) {
    btnLangToggle.textContent = currentLang === "hi" ? "🌐 हिन्दी" : "🌐 EN";
    btnLangToggle.addEventListener("click", () => {
      currentLang = currentLang === "en" ? "hi" : "en";
      localStorage.setItem("scenespeak_lang", currentLang);
      btnLangToggle.textContent = currentLang === "hi" ? "🌐 हिन्दी" : "🌐 EN";
      const announcement = currentLang === "hi" ? "भाषा बदलकर हिंदी कर दी गई है।" : "Language set to English.";
      speak(announcement);
    });
  }

  // Ambient Information Signals (AIS): Heading & Motion (PDR Section 10)
  let currentHeading = null;
  let isDeviceMoving = false;
  let lastMotionCheck = 0;

  if (window.DeviceOrientationEvent) {
    window.addEventListener("deviceorientation", (event) => {
      if (event.webkitCompassHeading) {
        currentHeading = Math.round(event.webkitCompassHeading);
      } else if (event.alpha !== null) {
        currentHeading = Math.round(360 - event.alpha);
      }
    }, { passive: true });
  }

  if (window.DeviceMotionEvent) {
    window.addEventListener("devicemotion", (event) => {
      const acc = event.acceleration;
      if (acc) {
        const magnitude = Math.sqrt((acc.x || 0)**2 + (acc.y || 0)**2 + (acc.z || 0)**2);
        if (magnitude > 1.8) {
          isDeviceMoving = true;
          lastMotionCheck = Date.now();
        } else if (Date.now() - lastMotionCheck > 400) {
          isDeviceMoving = false;
        }
      }
    }, { passive: true });
  }

  // Load saved speech rate preference
  let speechRate = parseFloat(localStorage.getItem("scenespeak_speech_rate") || "1.0");
  speechRateSlider.value = speechRate;
  rateValueLabel.textContent = `${speechRate.toFixed(1)}x`;

  speechRateSlider.addEventListener("input", (e) => {
    speechRate = parseFloat(e.target.value);
    rateValueLabel.textContent = `${speechRate.toFixed(1)}x`;
    localStorage.setItem("scenespeak_speech_rate", speechRate.toString());
  });

  // --- Camera Shutter Click Tone ---
  function playCameraShutterSound() {
    try {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioContext.state === "suspended") {
        audioContext.resume();
      }
      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(1000, audioContext.currentTime);
      osc.frequency.exponentialRampToValueAtTime(200, audioContext.currentTime + 0.08);

      gain.gain.setValueAtTime(0.3, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.08);

      osc.connect(gain);
      gain.connect(audioContext.destination);

      osc.start();
      osc.stop(audioContext.currentTime + 0.09);
    } catch (e) {
      // Ignored if audioContext not available
    }
  }

  // --- Web Audio Hazard Chime ---
  function playHazardAlertTone() {
    try {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioContext.state === "suspended") {
        audioContext.resume();
      }

      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(600, audioContext.currentTime);
      osc.frequency.exponentialRampToValueAtTime(300, audioContext.currentTime + 0.3);

      gain.gain.setValueAtTime(0.3, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

      osc.connect(gain);
      gain.connect(audioContext.destination);

      osc.start();
      osc.stop(audioContext.currentTime + 0.35);
    } catch (e) {
      console.warn("AudioContext error:", e);
    }
  }

  // --- Haptics ---
  function vibrate(pattern) {
    if ("vibrate" in navigator) {
      try {
        navigator.vibrate(pattern);
      } catch (e) {
        // Ignored on unsupported devices
      }
    }
  }

  // --- Speech Synthesis (TTS) ---
  function speak(text, onComplete) {
    if (!("speechSynthesis" in window)) {
      statusOutput.textContent = text;
      if (onComplete) onComplete();
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = speechRate;
    utterance.pitch = 1.0;
    utterance.lang = currentLang === "hi" ? "hi-IN" : "en-US";

    utterance.onstart = () => {
      statusOutput.textContent = text;
    };

    utterance.onend = () => {
      if (onComplete) onComplete();
    };

    utterance.onerror = (e) => {
      console.error("SpeechSynthesis error:", e);
      if (onComplete) onComplete();
    };

    window.speechSynthesis.speak(utterance);
  }

  // --- Camera Management ---
  async function startCamera() {
    try {
      cameraStatus.textContent = "Requesting rear camera...";
      const constraints = {
        video: {
          facingMode: { ideal: "environment" },
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      };

      currentStream = await navigator.mediaDevices.getUserMedia(constraints);
      video.srcObject = currentStream;
      await video.play();
      cameraStatus.style.display = "none";
    } catch (err) {
      console.warn("Rear camera error, attempting generic video:", err);
      try {
        currentStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        video.srcObject = currentStream;
        await video.play();
        cameraStatus.style.display = "none";
      } catch (fallbackErr) {
        cameraStatus.textContent = "Camera access denied or unavailable.";
        statusOutput.textContent = "Camera error. Please allow camera permissions.";
        speak("Camera access was denied. Please allow camera access in your browser settings.");
      }
    }
  }

  // --- Frame Capture & Resizing ---
  function captureFrame() {
    const videoWidth = video.videoWidth || 640;
    const videoHeight = video.videoHeight || 480;

    // Scale to max 768px on longest side (PDR Section 7.1)
    const maxDimension = 768;
    let targetWidth = videoWidth;
    let targetHeight = videoHeight;

    if (videoWidth > videoHeight) {
      if (videoWidth > maxDimension) {
        targetWidth = maxDimension;
        targetHeight = Math.round((videoHeight * maxDimension) / videoWidth);
      }
    } else {
      if (videoHeight > maxDimension) {
        targetHeight = maxDimension;
        targetWidth = Math.round((videoWidth * maxDimension) / videoHeight);
      }
    }

    canvas.width = targetWidth;
    canvas.height = targetHeight;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(video, 0, 0, targetWidth, targetHeight);

    // Return both the canvas element and base64 JPEG (quality 0.7)
    const imageB64 = canvas.toDataURL("image/jpeg", 0.7);
    return { canvas, imageB64, ctx, width: targetWidth, height: targetHeight };
  }

  // --- Client-Side Image Quality Checks (Section 7.1) ---
  function checkQuality(frame) {
    const { ctx, width, height } = frame;
    const imgData = ctx.getImageData(0, 0, width, height);
    const data = imgData.data;

    let totalLuminance = 0;
    const pixelCount = width * height;
    const grayscale = new Float32Array(pixelCount);

    for (let i = 0; i < pixelCount; i++) {
      const r = data[i * 4];
      const g = data[i * 4 + 1];
      const b = data[i * 4 + 2];
      // Standard luminance formula
      const lum = 0.299 * r + 0.587 * g + 0.114 * b;
      grayscale[i] = lum;
      totalLuminance += lum;
    }

    const meanLuminance = totalLuminance / pixelCount;

    // 1. Brightness Check
    if (meanLuminance < 20) {
      return {
        passed: false,
        reason: "The photo is too dark. Please aim towards light or turn on a room light and try again.",
      };
    }

    // 2. Blur Check via Laplacian Variance
    // Downsample for fast blur calculation
    let laplacianSum = 0;
    let laplacianSqSum = 0;
    let samples = 0;

    // Stride through image to evaluate sharpness
    const stride = 2;
    for (let y = 1; y < height - 1; y += stride) {
      for (let x = 1; x < width - 1; x += stride) {
        const center = grayscale[y * width + x];
        const top = grayscale[(y - 1) * width + x];
        const bottom = grayscale[(y + 1) * width + x];
        const left = grayscale[y * width + (x - 1)];
        const right = grayscale[y * width + (x + 1)];

        // Standard 3x3 discrete Laplacian operator
        const lap = top + bottom + left + right - 4 * center;
        laplacianSum += lap;
        laplacianSqSum += lap * lap;
        samples++;
      }
    }

    const lapMean = laplacianSum / samples;
    const lapVariance = (laplacianSqSum / samples) - (lapMean * lapMean);

    // If variance is extremely low, the image is severely blurred or featureless
    if (lapVariance < 15) {
      return {
        passed: false,
        reason: "The photo is too blurry. Please hold the phone steady and tap again.",
      };
    }

    return { passed: true };
  }

  // --- API Call ---
  async function callDescribeApi(mode, question = null, existingFrame = null) {
    let frame = existingFrame;
    if (!frame) {
      // Motion-based capture stabilization fallback
      if (isDeviceMoving) {
        await new Promise((resolve) => setTimeout(resolve, 300));
      }
      frame = captureFrame();
    }

    // Perform client-side quality verification
    const quality = checkQuality(frame);
    if (!quality.passed) {
      vibrate([100, 100]);
      statusOutput.textContent = quality.reason;
      speak(quality.reason, () => setBusy(false));
      return;
    }

    // Build Ambient Information Signals (AIS) Context (PDR Section 10)
    const context = {
      client_timestamp: new Date().toLocaleTimeString(),
      previous_scene_text: lastSpokenText || null,
      compass_heading: currentHeading,
      language: currentLang,
    };

    const payload = {
      image_b64: frame.imageB64,
      mode: mode,
      question: question,
      context: context,
    };

    try {
      const response = await fetch("/api/describe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        const spokenErr = errJson.detail?.spoken || errJson.spoken || "Server error. Please try again.";
        throw new Error(spokenErr);
      }

      const data = await response.json();
      lastRequestId = data.request_id;
      lastSpokenText = data.text;
      btnRepeat.disabled = false;
      feedbackRow.style.display = "flex";

      // Hazard Alert Handling
      if (data.hazard) {
        btnDescribe.classList.add("hazard-active");
        playHazardAlertTone();
        vibrate([200, 100, 200]);
      } else {
        btnDescribe.classList.remove("hazard-active");
      }

      // Read output aloud
      statusOutput.textContent = data.text;
      speak(data.text, () => setBusy(false));

    } catch (err) {
      console.error("Describe API failure:", err);
      const msg = err.message || "Could not connect to the scene service. Please check your network.";
      statusOutput.textContent = msg;
      speak(msg, () => setBusy(false));
    }
  }

  // --- Mode Handlers ---
  function triggerDescribe() {
    if (isProcessing) return;
    setBusy(true);
    playCameraShutterSound();
    vibrate(150);

    // Instant snapshot on tap: capture right away so user doesn't need to hold the camera steady
    const frame = captureFrame();

    const cue = currentLang === "hi" ? "देख रहा हूँ।" : "Looking.";
    speak(cue);
    callDescribeApi("describe", null, frame);
  }

  function triggerRead() {
    if (isProcessing) return;
    setBusy(true);
    playCameraShutterSound();
    vibrate(150);

    // Instant snapshot on tap
    const frame = captureFrame();

    const cue = currentLang === "hi" ? "पाठ पढ़ रहा हूँ।" : "Reading text.";
    speak(cue);
    callDescribeApi("read", null, frame);
  }

  function triggerAsk() {
    if (isProcessing) return;
    setBusy(true);
    playCameraShutterSound();
    vibrate(150);

    // Instant snapshot on tap: captured immediately so user can bring phone to mouth to speak
    const frame = captureFrame();

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
      const unsupported = currentLang === "hi"
        ? "इस ब्राउज़र में ध्वनि पहचान समर्थित नहीं है।"
        : "Speech recognition is not supported in this browser.";
      speak(unsupported, () => setBusy(false));
      return;
    }

    const askPrompt = currentLang === "hi" ? "आप क्या पूछना चाहते हैं?" : "What would you like to know?";
    speak(askPrompt, () => {
      const recognition = new SpeechRec();
      recognition.lang = currentLang === "hi" ? "hi-IN" : "en-US";
      recognition.continuous = false;
      recognition.interimResults = false;

      statusOutput.textContent = currentLang === "hi" ? "आपका प्रश्न सुना जा रहा है..." : "Listening for your question...";

      recognition.onresult = (event) => {
        const question = event.results[0][0].transcript;
        statusOutput.textContent = `Question: "${question}"`;
        const finding = currentLang === "hi" ? "उत्तर खोज रहा हूँ।" : "Finding answer.";
        speak(finding);
        callDescribeApi("ask", question, frame);
      };

      recognition.onerror = (e) => {
        console.error("SpeechRecognition error:", e);
        const errMsg = currentLang === "hi"
          ? "प्रश्न सुनाई नहीं दिया। कृपया पुनः प्रयास करें।"
          : "I could not hear your question. Please try again.";
        speak(errMsg, () => setBusy(false));
      };

      recognition.onnomatch = () => {
        const noMatchMsg = currentLang === "hi" ? "कोई आवाज़ सुनाई नहीं दी।" : "No speech recognized. Please try again.";
        speak(noMatchMsg, () => setBusy(false));
      };

      try {
        recognition.start();
      } catch (e) {
        const micErr = currentLang === "hi" ? "माइक उपलब्ध नहीं है।" : "Microphone is currently unavailable.";
        speak(micErr, () => setBusy(false));
      }
    });
  }

  function triggerRepeat() {
    if (!lastSpokenText) return;
    vibrate(100);
    speak(lastSpokenText);
  }

  // --- Feedback Handler ---
  async function submitFeedback(rating) {
    if (!lastRequestId) return;
    vibrate(100);
    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          request_id: lastRequestId,
          rating: rating,
          note: rating >= 4 ? "Helpful" : "Unhelpful",
        }),
      });
      speak("Feedback saved. Thank you.");
      feedbackRow.style.display = "none";
    } catch (e) {
      console.warn("Feedback submission failed:", e);
    }
  }

  // --- Busy State Toggle ---
  function setBusy(busy) {
    isProcessing = busy;
    btnDescribe.disabled = busy;
    btnRead.disabled = busy;
    btnAsk.disabled = busy;

    if (busy) {
      btnDescribe.classList.add("active");
    } else {
      btnDescribe.classList.remove("active");
    }
  }

  // --- Event Listeners ---
  btnDescribe.addEventListener("click", triggerDescribe);
  btnRead.addEventListener("click", triggerRead);
  btnAsk.addEventListener("click", triggerAsk);
  btnRepeat.addEventListener("click", triggerRepeat);
  btnFeedbackGood.addEventListener("click", () => submitFeedback(5));
  btnFeedbackBad.addEventListener("click", () => submitFeedback(1));

  // Auto-init camera and service worker on load
  window.addEventListener("DOMContentLoaded", () => {
    startCamera();

    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").then((reg) => {
        reg.update();
      }).catch((err) => {
        console.warn("ServiceWorker registration failed:", err);
      });
    }
  });

})();
