# SceneSpeak: Project Design Report (PDR)
Version: 1.0 (Hackathon MVP)  
Status: Draft for build  
Last updated: 24 September 2026  

---

## 1. Project Overview
SceneSpeak is a mobile-friendly web app (PWA) that lets a visually impaired user point their phone at their surroundings, tap one large button, and hear a short spoken description of what is in front of them.

| Item | Decision |
|---|---|
| **Platform** | Progressive Web App (runs in the phone browser, no app store) |
| **Intelligence** | Hosted vision-language model (VLM) accessed through an API |
| **Training** | None. Prompt engineering and evaluation only |
| **Audio** | Browser text-to-speech (free, built in) |
| **Hosting** | Single FastAPI service on a free cloud tier |

### Core modes
- **Describe**: general scene description with hazards first
- **Read**: reads text on signs, labels, menus
- **Ask**: answers a spoken question about the current photo

---

## 2. Problem Statement
Roughly 285 million people worldwide live with visual impairment. Existing solutions are:
- **Human-assisted services**: effective but need a live person, are not always available, and raise privacy concerns.
- **Traditional image captioning apps**: produce generic captions ("a room with furniture") that do not prioritize hazards, spatial layout, or readable text.
- **Specialized hardware**: expensive and not accessible in low-income regions.

**Gap**: There is no free, instant, phone-only tool that produces *audio-first, safety-aware, spatially grounded* descriptions.

---

## 3. Objective & Measurable Goals
Primary objective: Deliver a working MVP in a hackathon window where a user taps once and hears a useful scene description in under 4 seconds.

| # | Goal | Target |
|---|---|---|
| G1 | End-to-end latency (tap to speech start) | ≤ 4 s on mobile data |
| G2 | Description length | ≤ 3 short sentences |
| G3 | Usable without looking at the screen | Passes TalkBack/VoiceOver test |
| G4 | Quality on real blind-user photos (VizWiz sample) | ≥ 3.5 / 5 average on rubric |
| G5 | Handles bad images gracefully | 100% of blurry/dark test images trigger a "please retake" message |
| G6 | Deployed on public HTTPS URL | Yes |

*Non-goals*: navigation, replacing a cane or guide dog, offline mode, custom model training, native apps.

---

## 4. System Architecture
```text
┌────────────── Phone Browser (PWA) ──────────────┐
│  UI: big buttons + ARIA labels                  │
│  Camera capture -> resize -> quality check      │
│  Ambient signals: GPS / compass / time (opt.)   │
│  TTS (speak result)   STT (voice question)      │
└──────────────────┬──────────────────────────────┘
                   │ HTTPS  POST /api/describe
┌──────────────────▼──────────────────────────────┐
│  FastAPI Backend                                │
│  1. Validate request (size, type, mode)         │
│  2. Build prompt (mode + context)               │
│  3. Call VLM provider (key stays server-side)   │
│  4. Post-process text, detect retake/hazard     │
│  5. Log metadata to SQLite (no images)          │
└───────────┬─────────────────────┬───────────────┘
            │                     │
   ┌────────▼─────────┐   ┌───────▼────────┐
   │  Vision-language │   │  SQLite (logs, │
   │  model API       │   │  feedback)     │
   └──────────────────┘   └────────────────┘
```
