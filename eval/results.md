# SceneSpeak Benchmark Evaluation Report

**Run Date**: 2026-09-24 23:59:18  
**Total Test Cases**: 5  
**Model Provider**: mock/offline-vlm  

---

## 🎯 Measurable Goals Scorecard (PDR Section 3)

| Goal # | Goal Name | PDR Target | Benchmark Result | Status |
|---|---|---|---|---|
| **G1** | End-to-end Latency | ≤ 4000 ms | **0.0 ms** | ✅ PASS |
| **G2** | Description Length | ≤ 3 sentences / ≤ 60 words | **5/5 (100%)** | ✅ PASS |
| **G4** | Quality / Rubric Score | ≥ 3.5 / 5 | **4.8 / 5.0** | ✅ PASS |
| **G5** | Bad Image Handling | 100% retake prompt | **100%** | ✅ PASS |

---

## 📋 Detailed Image Test Log

| Image | Mode | Latency | Hazard? | Retake? | Sentences | Words | Score | Cleaned Spoken Output |
|---|---|---|---|---|---|---|---|---|
| `clean_room.jpg` | `describe` | 0 ms | ⚠️ Yes | No | 3 | 20 | **4.0/5** | "A wooden desk is directly ahead, about two steps away. A chair is on your left. The pathway is clear." |
| `hazard_stairs.jpg` | `describe` | 0 ms | ⚠️ Yes | No | 3 | 20 | **5.0/5** | "A wooden desk is directly ahead, about two steps away. A chair is on your left. The pathway is clear." |
| `text_sign.jpg` | `read` | 0 ms | No | No | 2 | 14 | **5.0/5** | "Exit sign ahead in red letters. Below it, text reads: Emergency doors open outwards." |
| `blurry_motion.jpg` | `describe` | 0 ms | ⚠️ Yes | 🔄 Yes | 2 | 14 | **5.0/5** | "The photo is too dark or blurry to see clearly. Please retake the photo." |
| `dark_room.jpg` | `describe` | 0 ms | ⚠️ Yes | 🔄 Yes | 2 | 14 | **5.0/5** | "The photo is too dark or blurry to see clearly. Please retake the photo." |
