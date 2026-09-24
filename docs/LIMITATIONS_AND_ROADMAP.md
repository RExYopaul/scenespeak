# SceneSpeak: Honest Limitations & Engineering Roadmap

This document outlines the known limitations (PDR Section 17) and engineering roadmap (PDR Section 18) for SceneSpeak.

---

## ⚠️ Known Limitations & Mitigations (PDR Section 17)

| # | Limitation | Impact on User | Mitigation Built into SceneSpeak |
|---|---|---|---|
| **L1** | **VLM Hallucination** | Model could occasionally mention objects not present. | Strict system prompt: *"If unsure, say 'it looks like'. Never guess."* Explicit visual hedging. |
| **L2** | **Not Safety-Critical** | Distances and obstacle coordinates are rough estimates. | Clear audio and visual disclaimer: SceneSpeak is an orientation aid, **not a replacement for a white cane or guide dog**. |
| **L3** | **Internet Connectivity Required** | Cannot process scenes when offline. | Documented non-goal for MVP. Graceful spoken error: *"Network unavailable. Please check your connection."* (On-device model planned for roadmap). |
| **L4** | **Latency (2–4 seconds)** | Not instant/real-time streaming. | Immediate tactile vibration + spoken *"Looking."* within 200 ms so user knows system is actively working. |
| **L5** | **Cloud Privacy** | Image bytes travel across HTTPS to vision model API. | **Privacy by Default**: EXIF stripped client-side, images processed in-memory only, **zero** images stored in database or filesystem. |
| **L6** | **Browser Speech Differences** | Speech recognition (STT) varies on Safari/iOS. | Core **Describe** and **Read** modes work universally without microphone input. Ask mode gracefully notifies if STT is unsupported. |
| **L7** | **Free-Tier Cold Starts** | Free cloud tier may sleep after 15 minutes of inactivity. | Automated ping / pre-demo warm-up protocol; demo video backup prepared. |
| **L8** | **Limited Pilot Evaluation** | Tested on benchmark subset (30–50 scenes) rather than clinical trial. | Reported honestly as an assistive pilot prototype ready for user-study testing. |
| **L9** | **Language Support** | English-first in current build. | Multilingual prompt expansion (Hindi, Spanish, etc.) is the top near-term priority. |
| **L10**| **Viewfinder Framing** | Visually impaired user cannot see if photo is aimed properly. | Client-side blur check and brightness check immediately catch unusable frames before calling the server. |

---

## 🗺️ Engineering Roadmap (PDR Section 18)

### Near-Term (Weeks 1–2)
- **Hindi & Vernacular Speech Support**: Add multilingual prompt templates and select localized TTS voices (`hi-IN`).
- **Continuous Scan Mode**: Auto-capture frame every 4 seconds, comparing against previous scene memory to only announce new changes.
- **Audio Framing Guidance**: Detect if light source is direct or camera is covered, giving spoken cues (*"Aim slightly to your left"*).

### Mid-Term (Months 1–3)
- **Haptic Spatial Cues**: Multi-pattern vibration pulses indicating directional distance (left vs. right obstacle).
- **Personal Object Locator**: Memory-assisted queries (*"Where did I leave my keys?"*).
- **Persistent User Accounts**: Optional PostgreSQL cloud database to preserve custom voice settings and history across devices.
- **Native Mobile Wrapper**: Package via Capacitor / React Native for deeper OS accessibility shortcuts (e.g. volume button press triggers describe).

### Long-Term (Months 3–12)
- **On-Device Edge Vision Models**: Run lightweight quantized vision models (e.g. MobileNet / Gemma Vision) directly on-device for 100% offline capability and zero cloud latency.
- **Smart Glasses Integration**: Connect with smart glasses (Meta Ray-Ban style hardware) for hands-free assistive vision.
- **Live Bidirectional Video Streaming**: Integrate WebSockets Live API for continuous conversational scene guidance.
