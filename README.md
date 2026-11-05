# PROJECT RIA — Research Intelligence Aariz
### Sustainable Research Intelligence & Universal Physics Lab — SDG 7, 9, 11, 12, 13

**PROJECT RIA (Research Intelligence Aariz)** is an integrated scientific pair-computing platform that unites:
1. **Interactive 2D Rigid-Body Physics Lab (Pymunk / Chipmunk2D):** Natural-language apparatus construction, enclosed chamber boundaries, zero-torque mouse interaction, live $60\text{ FPS}$ telemetry, and automated scientific conclusion generation.
2. **Sustainable Research Intelligence Suite (SDG 7, 9, 11, 12, 13):** Autonomous scholarly research fellow with keyless arXiv and CrossRef academic search, document ingestion/summarization, cross-domain physics data synthesis, and conceptual schematic generation.
3. **Multimodal Vision ("Image-to-Simulation"):** Translates sketches, diagrams, and textbook plots into active physics simulations or quantitative graph analyses via OpenAI (GPT-4o) and Google Gemini.
4. **Image Generation Engine:** Renders technical engineering blueprints and architectural prototype schematics via DALL-E 3 and Gemini Imagen 3.

---

## 🏛️ System Architecture

```
                                  ┌───────────────────────────────────────────────────┐
                                  │      PROJECT RIA Unified Desktop Application      │
                                  └─────────────────────────┬─────────────────────────┘
                                                            │
                       ┌────────────────────────────────────┴────────────────────────────────────┐
                       ▼                                                                         ▼
   ┌───────────────────────────────────────┐                                 ┌───────────────────────────────────────┐
   │     [ ⚛ Physics Simulation Lab ]      │                                 │  [ 🌱 Sustainable Research Suite ]    │
   ├───────────────────────────────────────┤                                 ├───────────────────────────────────────┤
   │ • 40:60 CustomTkinter Split View      │                                 │ • Document & Report Ingestion Zone    │
   │ • AIAgent Tool Calling (OpenAI/Qwen)  │                                 │ • ResearchAgent Academic Fellow       │
   │ • Pymunk Rigid Bodies & Enclosed Room │                                 │ • Live arXiv & CrossRef DOI Search    │
   │ • Zero-Torque Mouse Grab & Rotation   │                                 │ • 1-Click SDG Dossiers (7, 9, 12, 13) │
   │ • Dynamic Telemetry & Control Sheet   │                                 │ • Cross-Domain Physics Data Bridge    │
   │ • Image-to-Simulation Diagram Parser  │                                 │ • Concept Schematic Engine (Imagen/D3)│
   └───────────────────────────────────────┘                                 └───────────────────────────────────────┘
```

---

## ✨ Key Capabilities & Innovations

1. **Deterministic Scientific Accuracy (Zero Math Hallucination):**
   * The LLM **never calculates equations internally**. Instead, it acts as an apparatus architect, invoking structured tools (`create_wedge`, `create_box`, `create_circle`, `create_joint`, `apply_force`, `set_experiment_metrics`).
   * The actual mathematical equations of motion, gravity, friction, and momentum are computed by **Pymunk** at 60 FPS.

2. **Laboratory Experiment Protocol (Setup Freeze at $t=0.00\text{s}$):**
   * The engine automatically freezes apparatus at $t=0.00\text{s}$ upon generation.
   * Motion only begins when you click **`[▶ Release / Run]`**, preventing experiments from running while the AI is thinking.
   * A **`[↺ Reset (t=0)]`** button restores bodies to their initial state for repeatable trials.

3. **Light Modern Laboratory Aesthetic:**
   * High-clarity laboratory viewport with soft off-white background (`#f8fafc`) and subtle engineering grid lines.
   * One-click theme toggle: switch between **☀️ Light Lab** and **🌙 Dark Mode** anytime.

4. **Dynamic Telemetry & Formal Control Sheet:**
   * No hardcoded static metrics: cards adapt dynamically to whatever variables the experiment measures (Velocity, Acceleration, Height, Kinetic Energy, Momentum, Normal Force).
   * Features fuzzy body matching and automatic fallback telemetry.
   * Clicking **`[📋 Report]`** generates a formal **Experiment Control Sheet** with title, aim, theoretical formula, duration, peak velocity, average velocity, and an engineering conclusion.

5. **10 Demonstration-Ready Preset Experiments (1-Click Switcher):**
   * Instant dropdown in the viewport header:
     1. *Galileo's Free Fall (10kg vs 2kg side-by-side)*
     2. *Incline Friction & Sled (Solid Wedge with Coulomb friction)*
     3. *Newton's Cradle (5-ball momentum transfer chain)*
     4. *2-Body Elastic Collision & Velocity Exchange*
     5. *Structural Truss Bridge Deflection (SDG 9 Infrastructure)*
     6. *Simple Harmonic Motion (Pendulum period invariance)*
     7. *High-Friction Skid & Braking Distance*
     8. *Catapult / Lever Arm Projectile Launch*
     9. *Bouncing Ball Coefficient of Restitution ($e$) Decay*
     10. *Wrecking Ball & Structural Demolition*

6. **Dual AI Backend (Cloud + Local Offline):**
   * Supports **OpenAI API** (`gpt-4o-mini`, `gpt-4o`).
   * Supports local **Ollama** (`qwen3.5:9b`, `mythos-9b`) for 100% offline, privacy-first, zero-cost execution on Apple Silicon.

---

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Lab
```bash
python3 main.py
```

### 3. Configure Model / API
* Click **⚙ Settings & Presets** at the bottom-left.
* Choose **OpenAI Default** (enter API key) or **Local Ollama** (with one click).

---

## 🌍 SDG 9 Alignment (Industry, Innovation & Infrastructure)
* **Democratizing Scientific Simulation:** Makes engineering experimentation accessible through conversation rather than complex proprietary GUI software.
* **Virtual Prototyping:** Allows testing structural integrity, transport friction, and momentum transfer in a zero-cost sandbox.
* **Traceable Engineering Telemetry:** Connects high-level qualitative prompts to quantitative, verified physical data.
