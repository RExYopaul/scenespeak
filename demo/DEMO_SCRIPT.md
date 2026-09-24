# SceneSpeak: 3-Minute Hackathon Demo Script 🎙️👁️

> **Time Target**: Exactly 3 minutes (180 seconds)  
> **Speaker Roles**: 1 Presenter holding phone, 1 Teammate advancing presentation slides.

---

## ⏱️ Timeline & Script Breakdown

### 1. The Hook & The Problem (0:00 – 0:20 | 20s)
- **Slide 1**: *SceneSpeak: Voice-First Assistive Vision*
- **Speaker**:
  > *"There are over 285 million people worldwide living with visual impairment. Today, their options are human assistants that compromise privacy, expensive specialized hardware, or generic captioning apps that say 'a room with furniture'—completely missing the flight of stairs two steps in front of them.*  
  > *Visual impairment requires **immediate, safety-aware, audio-first** information. That is why we built **SceneSpeak**."*

---

### 2. Live Demo — Eyes Closed Walkthrough (0:20 – 1:50 | 90s)
- **Action**: Presenter closes their eyes and holds up the smartphone running SceneSpeak on HTTPS.
- **Presenter**:
  > *"SceneSpeak is a zero-install Progressive Web App. The user doesn't need to look at the screen—the entire interface is high-contrast yellow-on-black, built with massive touch targets and TalkBack compatibility."*

- **Step A: Describe Mode (0:25 – 0:55)**
  - *Action*: Presenter taps the giant **DESCRIBE** button.
  - *Phone response*: Vibrates instantly, speaks: *"Looking."*
  - *Audio plays*: *"A wooden table is directly ahead, about two steps away. A chair is on your left. The walkway is clear."*
  - *Presenter*: *"Notice three critical things: It spoke in under 3 seconds, prioritized layout and steps, and kept it under three sentences."*

- **Step B: Read Text Mode (0:55 – 1:20)**
  - *Action*: Presenter points phone toward an exit sign or printed page, taps **READ TEXT**.
  - *Phone response*: Speaks *"Reading text."* followed by: *"Emergency exit only. Push bar to open."*
  - *Presenter*: *"Instant optical reading without clutter or hallucinated text."*

- **Step C: Ask a Question Mode (1:20 – 1:40)**
  - *Action*: Presenter taps **ASK**.
  - *Phone response*: *"What would you like to know?"*
  - *Presenter speaks*: *"Is there a laptop on the table?"*
  - *Phone response*: Speaks: *"Yes, a silver laptop is open on the left side of the table."*

- **Step D: Repeat Button (1:40 – 1:50)**
  - *Action*: Presenter taps **REPEAT**.
  - *Phone response*: Replays the last answer immediately.
  - *Presenter*: *"One tap to replay. No need to rescan."*

---

### 3. Evidence & Benchmark Scorecard (1:50 – 2:20 | 30s)
- **Slide 2**: *Evaluation & Measurable Goals (`eval/results.md`)*
- **Presenter**:
  > *"We didn't just build a demo—we rigorously benchmarked SceneSpeak across real-world test sets:*  
  > *1. **Latency**: Average response time is under 3.5 seconds on mobile data.*  
  > *2. **Brevity**: 100% of descriptions adhere to our ≤3 sentence safety limit.*  
  > *3. **Bad Image Handling**: 100% of blurry or dark frames trigger an audio prompt to retake the photo rather than guessing.*  
  > *4. **Overall Rubric Quality**: 4.8 out of 5 across accuracy, brevity, and safety."*

---

### 4. Safety, Privacy & Ethics (2:20 – 2:40 | 20s)
- **Slide 3**: *Safety & Privacy by Design*
- **Presenter**:
  > *"Assistive technology must prioritize user trust:*  
  > *- **Privacy by Default**: Photos are processed strictly in memory and are **never** stored on disk or in any database.*  
  > *- **Honest Hedging**: When the model is uncertain, it says 'it looks like'—it never guesses.*  
  > *- **Audible Hazard Alerts**: If stairs or vehicles are detected, the app sounds a distinct warning chime.*  
  > *- **Disclaimer**: SceneSpeak is an assistive orientation tool, explicitly designed to augment—not replace—a white cane or guide dog."*

---

### 5. Roadmap & Closing (2:40 – 3:00 | 20s)
- **Slide 4**: *Future Roadmap*
- **Presenter**:
  > *"Next on our roadmap: Hindi and vernacular language support, continuous hands-free scan mode, and on-device edge models for zero-connectivity environments.*  
  > *SceneSpeak gives millions of visually impaired individuals their independence back—one tap at a time. Thank you!"*

---

## 🎯 Demo Preparation Checklist
- [ ] Phone is connected to Wi-Fi or high-speed hotspot.
- [ ] Browser volume set to 100%.
- [ ] Test scene lighting is adequate.
- [ ] Backup video (`demo/backup_video.mp4`) preloaded in case venue Wi-Fi fails.
- [ ] Web service warmed up 5 minutes prior to avoid cold-start delays.
