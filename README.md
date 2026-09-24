# SceneSpeak 👁️🔊

> **Voice-First Assistive Scene Description for the Visually Impaired**

SceneSpeak is an accessible, mobile-friendly Progressive Web App (PWA) that allows visually impaired users to point their smartphone at their surroundings, tap once, and hear an audio-first, safety-aware, spatially grounded description in under 4 seconds.

---

## 🌟 Key Features

- **Audio-First Design**: Auto-speaks scene descriptions; complete screen-reader compatibility (TalkBack / VoiceOver).
- **Hazard-First Prioritization**: Obstacles and safety hazards (stairs, curbs, approaching vehicles, wet floors) are prioritized before general layout.
- **Three Core Modes**:
  1. **Describe**: Full spatial layout and hazard overview.
  2. **Read**: Instant reading of text on signs, food packaging, and labels.
  3. **Ask**: Natural voice-driven Q&A about the surroundings.
- **Client-Side Quality Gate**: Rejects blurry or underexposed photos before wasting API calls.
- **Privacy by Default**: Photos are processed strictly in-memory and are **never** saved to disk or database.
- **Offline Mock Fallback**: Runs immediately out of the box without requiring external API keys.

---

## 📁 Project Structure

```text
SceneSPEAK_antiGravity/
├── backend/                  # FastAPI Python backend
│   ├── app/                  # Core modules
│   │   ├── main.py           # FastAPI routes & static file mounting
│   │   ├── config.py         # App settings & environment loader
│   │   ├── prompts.py        # System prompts for Describe, Read, and Ask
│   │   ├── vlm.py            # Vision model interface (Gemini & OpenAI)
│   │   ├── postprocess.py    # Markdown removal, sentence limits, hazard flags
│   │   ├── db.py             # SQLite persistence (No images stored)
│   │   └── schemas.py        # Pydantic data contracts
│   ├── tests/                # Automated pytest suite (13 passing tests)
│   │   ├── test_describe.py
│   │   ├── test_postprocess.py
│   │   └── test_error_handling.py
│   ├── test_cli.py           # Single-image command-line tester
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment configuration template
├── frontend/                 # High-contrast accessible PWA
│   ├── index.html            # Semantic accessible UI with ARIA live regions
│   ├── style.css             # Yellow-on-black WCAG AAA styling
│   ├── app.js                # Camera capture, quality check, TTS & audio
│   ├── sw.js                 # Service worker for offline caching
│   ├── manifest.json         # PWA home screen installation
│   └── icons/                # High-contrast app icons
├── eval/                     # Evaluation & benchmarking harness
│   ├── images/               # Benchmark test images
│   ├── run_eval.py           # Automated evaluation runner
│   ├── results.csv           # Evaluation results data
│   └── results.md            # Benchmark scorecard
├── demo/                     # Demo script & presentation materials
│   └── DEMO_SCRIPT.md        # 3-minute hackathon pitch script
├── docs/                     # Documentation & specifications
│   ├── SceneSpeak_PDR.md     # Full Project Design Report
│   └── LIMITATIONS_AND_ROADMAP.md # Limitations and future roadmap
├── render.yaml               # 1-Click Render cloud deployment
├── Dockerfile                # Production Docker container
├── Procfile                  # Procfile for web hosting
├── README.md                 # Project documentation
└── .gitignore                # Protects secrets and virtual environment
```

---

## 🚀 Quickstart for Beginners

### 1. Set Up the Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### 2. Run the Local Development Server
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open **`http://localhost:8000`** in your browser (Google Chrome or Microsoft Edge recommended).

---

## 🧪 Testing & Evaluation

### Run the Automated Test Suite (13 Tests)
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests
```

### Test Any Single Image via CLI
```powershell
.\.venv\Scripts\python.exe backend/test_cli.py --image eval/images/hazard_stairs.jpg --mode describe
```

### Run the Benchmark Evaluation Suite
```powershell
.\.venv\Scripts\python.exe eval/run_eval.py
```
This tests all benchmark scenes against the PDR measurable goals and generates [`eval/results.md`](file:///c:/Users/Dell/OneDrive/12th%20boards%202025/SceneSPEAK_antiGravity/eval/results.md).

---

## 🔑 Connecting a Live Vision Model (Optional)

SceneSpeak works out-of-the-box in mock mode. To connect a live model:
1. Copy the environment template:
   ```powershell
   Copy-Item backend/.env.example backend/.env
   ```
2. Add your API key in `backend/.env`:
   ```ini
   VLM_PROVIDER=gemini
   VLM_API_KEY=YOUR_GEMINI_API_KEY
   VLM_MODEL=gemini-2.0-flash
   ```

---

## ☁️ Cloud Deployment (HTTPS Required for Camera)

Browsers restrict camera access to `localhost` and `HTTPS` domains.

### Option A: Render (1-Click Blueprint)
1. Push this repository to GitHub.
2. Log into [Render](https://render.com) and click **New > Blueprint**.
3. Select this repo—Render will automatically read [`render.yaml`](file:///c:/Users/Dell/OneDrive/12th%20boards%202025/SceneSPEAK_antiGravity/render.yaml) and configure the service.
4. Set the `VLM_API_KEY` secret in the Render dashboard.

### Option B: Docker
```bash
docker build -t scenespeak .
docker run -p 8000:8000 scenespeak
```

---

## 🎙️ Hackathon Demo Plan

A complete 3-minute pitch script with timing, slide notes, and live eyes-closed demo instructions is available in [`demo/DEMO_SCRIPT.md`](file:///c:/Users/Dell/OneDrive/12th%20boards%202025/SceneSPEAK_antiGravity/demo/DEMO_SCRIPT.md).
