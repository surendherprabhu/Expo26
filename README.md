# Universal AI Simulation Environment (Expo26)
### SDG 9 — Industry, Innovation and Infrastructure

An AI-powered 2D rigid-body simulation environment where users can create, modify, inspect, and interact with physical and engineering systems using natural language.

---

## 🚀 Features

- **40:60 Split Architecture:**
  - **Left Pane (40%):** Conversational AI interface, live tool execution logs, and demo scenario presets.
  - **Right Upper Pane:** High-performance 2D Pymunk physics viewport rendered at 60 FPS.
  - **Right Lower Pane:** Real-time engineering statistics & measurements ($E_k$, $E_p$, Total Mechanical Energy, active objects, velocity).
- **Interactive Mouse Physics:** Click, grab, and fling any object in the simulation canvas with your mouse.
- **OpenAI Tool Calling:** Uses structured function calling (`create_box`, `create_circle`, `create_ramp`, `create_joint`, `apply_force`, `set_world_gravity`) with fallback offline heuristics.
- **CustomTkinter Dark Aesthetic:** Matches the R.A.P.H.A.E.L UI design with `#050d1e` background, rounded borders, and emerald green (`#2fa572`) accents.
- **Simulation Controls:** Pause/Play, Earth / Moon / Zero-G gravity switching, and quick reset.

---

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Application
```bash
python3 main.py
```

### 3. Configure OpenAI API Key
- Click the **⚙ Settings** button in the bottom-left corner.
- Paste your OpenAI API key and choose your model (e.g. `gpt-4o-mini` or `gpt-4o`).
- If no key is provided, the application runs in **Offline Mode** with built-in engineering presets and heuristics.

---

## 🧪 Try These Prompts

- *"Build a 5-ball Newton's Cradle and launch the first bob."*
- *"Construct an inclined ramp with a rolling sphere and a sliding block."*
- *"Build a 3-segment pinned bridge deck spanning a 480px gap with a 35kg test load dropping on the midpoint."*
- *"Stack a 5-block vertical tower."*
- *"Set gravity to zero and apply an upward force to the ball."*
