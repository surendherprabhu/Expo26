# PROJECT RIA — Research Intelligence Aariz
### Universal AI Simulation Lab — SDG 9: Industry, Innovation & Infrastructure

**PROJECT RIA (Research Intelligence Aariz)** is an AI-powered simulation environment that connects Large Language Models (OpenAI or Local Ollama) to a verified 2D rigid-body scientific physics engine (Pymunk / Chipmunk2D). Users can construct, modify, inspect, and run actual mechanical experiments conversationally in real time.

---

## 🏛️ System Architecture

```
                  ┌───────────────────────────────────────────────┐
                  │   User Conversational Prompt & UI Controls    │
                  └───────────────────────┬───────────────────────┘
                                          │ (Natural Language)
                                          ▼
                  ┌───────────────────────────────────────────────┐
                  │            AIAgent (LLM Controller)           │
                  │       OpenAI (gpt-4o-mini) / Ollama (Qwen)    │
                  │   Structured Tool Calling (JSON Schema API)   │
                  └───────────────────────┬───────────────────────┘
                                          │ (Typed Physical Action Tools)
                                          ▼
                  ┌───────────────────────────────────────────────┐
                  │           PhysicsEngine (Pymunk 2D)           │
                  │   • Solid Triangular Wedges & Incline Planes  │
                  │   • Rigid Bodies, Masses, Moments of Inertia  │
                  │   • Pin Joints, Springs, and Kinematics       │
                  │   • Setup Freeze at t=0.0s & Snapshot State   │
                  │   • Live Telemetry (v, a, h, Ek, Ep, p, Fn)   │
                  └───────────────┬───────────────────────┬───────┘
                                  │                       │
      (Offscreen Pygame Rendering)▼                       ▼ (Telemetry / Data Stream)
         ┌──────────────────────────────┐   ┌──────────────────────────────┐
         │     PhysicsRenderer (PIL)    │   │  StatsPanel (Dynamic Cards)  │
         │  • Light Laboratory Theme    │   │  • 60 FPS Real-Time Cards    │
         │  • Dark Mode Toggle          │   │  • Experiment Control Sheet  │
         │  • Mouse Grab & Fling Engine │   │  • Scientific Report Mode    │
         └───────────────┬──────────────┘   └───────────────┬──────────────┘
                         │                                  │
                         └─────────────────┬────────────────┘
                                           ▼
                  ┌───────────────────────────────────────────────┐
                  │    CustomTkinter 40:60 Split User Interface   │
                  │      (Dark Aesthetic matching R.A.P.H.A.E.L)  │
                  └───────────────────────────────────────────────┘
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
