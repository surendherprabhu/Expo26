"""
Preset Experiments Library for Universal AI Simulation Environment (SDG 9).
Defines rigorous scientific experiments with defined aims, apparatus specifications,
theoretical equations, and verified conclusions.
"""

from typing import Dict, Any, List

PRESET_EXPERIMENTS: List[Dict[str, Any]] = [
    {
        "id": "incline_friction",
        "title": "1. Newton's Second Law & Friction on an Inclined Plane",
        "aim": "Verify the equation a = g(sin θ - μ cos θ) by measuring the acceleration of a wooden block sliding down a 30° solid wedge with kinetic friction μ = 0.35.",
        "theoretical_benchmark": "a_theor = 9.0 * (sin 30° - 0.35 * cos 30°) = 1.77 m/s²",
        "conclusion": "Observed acceleration confirms Newton's Second Law and Coulomb friction. Normal force Fn = mg cos θ directly governs kinetic friction resistance (SDG 9 Sustainable Manufacturing).",
        "metrics": [
            {"id": "theta", "name": "Incline Angle (θ)", "unit": "°", "type": "constant", "value": 30.0},
            {"id": "mu", "name": "Friction Coeff (μ)", "unit": "", "type": "constant", "value": 0.35},
            {"id": "v_block", "name": "Block Velocity (v)", "target_body": "wooden_block", "type": "velocity", "unit": "m/s"},
            {"id": "a_block", "name": "Acceleration (a)", "target_body": "wooden_block", "type": "accel", "unit": "m/s²"},
            {"id": "fn", "name": "Normal Force (Fn)", "target_body": "wooden_block", "type": "normal_force", "unit": "N", "value": 30.0}
        ],
        "setup_function": "load_incline_friction"
    },
    {
        "id": "elastic_collision",
        "title": "2. Conservation of Linear Momentum in 2-Body Impact",
        "aim": "Demonstrate the conservation of total linear momentum (p = m1*v1 + m2*v2) and velocity exchange during an elastic collision between a moving striker and stationary target.",
        "theoretical_benchmark": "Total Momentum p_initial = m1 * v1_initial = const; e = (v2' - v1') / (v1 - v2) ≈ 0.98",
        "conclusion": "Total momentum is conserved across the impact interface with minimal mechanical energy loss, validating kinetic energy transmission in machinery (SDG 9).",
        "metrics": [
            {"id": "m_ratio", "name": "Mass Ratio (m1/m2)", "unit": "", "type": "constant", "value": 2.67},
            {"id": "v_striker", "name": "Striker Velocity (v1)", "target_body": "striker_sphere", "type": "velocity", "unit": "m/s"},
            {"id": "v_target", "name": "Target Velocity (v2)", "target_body": "target_sphere", "type": "velocity", "unit": "m/s"},
            {"id": "a_striker", "name": "Impact Decel (a1)", "target_body": "striker_sphere", "type": "accel", "unit": "m/s²"}
        ],
        "setup_function": "load_elastic_collision"
    },
    {
        "id": "truss_bridge",
        "title": "3. Structural Truss Bridge Deflection (SDG 9 Infrastructure)",
        "aim": "Evaluate load distribution, joint deflection, and dynamic shock absorption of a 3-segment pinned bridge deck spanning a 480px gap under a 35 kg concentrated impact.",
        "theoretical_benchmark": "Static Equilibrium: ΣFy = 0, Pier Reactions R1 = R2 = 0.5 * W_total ≈ 310 N",
        "conclusion": "Pinned joints distribute vertical bending stresses across adjacent deck members to the foundation piers, preventing catastrophic structural failure (SDG 9 Resilient Infrastructure).",
        "metrics": [
            {"id": "span", "name": "Span Length", "unit": "m", "type": "constant", "value": 4.80},
            {"id": "deck_mass", "name": "Total Deck Mass", "unit": "kg", "type": "constant", "value": 34.0},
            {"id": "load_mass", "name": "Concentrated Load", "unit": "kg", "type": "constant", "value": 35.0},
            {"id": "v_load", "name": "Load Velocity (v)", "target_body": "impact_load", "type": "velocity", "unit": "m/s"}
        ],
        "setup_function": "load_truss_bridge"
    },
    {
        "id": "pendulum_shm",
        "title": "4. Simple Harmonic Motion & Tuned Mass Damping",
        "aim": "Verify that the oscillation period of a pendulum is governed by effective length T = 2π√(L/g) and independent of bob mass for small displacements.",
        "theoretical_benchmark": "Theoretical Period T = 2π * √(2.2 / 9.0) = 3.10 s",
        "conclusion": "Gravitational restoring torque τ = -mgL sin θ produces periodic oscillation. Fundamental to tuned mass dampers used to stabilize high-rise infrastructure against wind/earthquakes (SDG 9 & 11).",
        "metrics": [
            {"id": "arm_len", "name": "Pendulum Length (L)", "unit": "m", "type": "constant", "value": 2.20},
            {"id": "bob_m", "name": "Bob Mass (m)", "unit": "kg", "type": "constant", "value": 6.0},
            {"id": "v_bob", "name": "Linear Velocity (v)", "target_body": "pendulum_bob", "type": "velocity", "unit": "m/s"},
            {"id": "a_bob", "name": "Centripetal Accel (ac)", "target_body": "pendulum_bob", "type": "accel", "unit": "m/s²"}
        ],
        "setup_function": "load_pendulum_shm"
    }
]

def load_preset_by_id(physics_engine, preset_id: str) -> Dict[str, Any]:
    """Loads a verified experiment into the physics engine and freezes at t=0."""
    physics_engine.reset()
    
    preset = next((p for p in PRESET_EXPERIMENTS if p["id"] == preset_id), PRESET_EXPERIMENTS[0])
    
    physics_engine.experiment_metadata = {
        "title": preset["title"],
        "aim": preset["aim"],
        "theoretical_benchmark": preset["theoretical_benchmark"],
        "conclusion": preset["conclusion"]
    }
    
    if preset_id == "incline_friction":
        # Solid wedge: x_left=80, x_right=500, height=242.5 (30 deg slope)
        physics_engine.add_wedge("solid_wedge", 80, 500, 242.5, friction=0.35, elasticity=0.2)
        physics_engine.add_box("wooden_block", 0, 0, 40, 28, mass=6.0, friction=0.35, elasticity=0.1, color=(210, 140, 70), on_wedge="solid_wedge")
        
    elif preset_id == "elastic_collision":
        # Runway floor
        physics_engine.add_segment("runway", 40, 440, 720, 440, thickness=10, friction=0.05, elasticity=0.98)
        # Striker sphere (left)
        physics_engine.add_circle("striker_sphere", 140, 415, 25, mass=8.0, friction=0.05, elasticity=0.98, color=(46, 204, 113))
        # Target sphere (mid)
        physics_engine.add_circle("target_sphere", 380, 420, 18, mass=3.0, friction=0.05, elasticity=0.98, color=(52, 152, 219))
        # Initial impulse to launch striker
        physics_engine.apply_impulse("striker_sphere", (3200, 0))
        
    elif preset_id == "truss_bridge":
        # Piers
        physics_engine.add_box("pier_left", 140, 380, 70, 140, static=True, color=(100, 110, 120))
        physics_engine.add_box("pier_right", 620, 380, 70, 140, static=True, color=(100, 110, 120))
        # 3 deck segments
        physics_engine.add_box("deck_1", 240, 315, 120, 16, mass=10.0, color=(46, 204, 113))
        physics_engine.add_box("deck_2", 380, 315, 160, 16, mass=14.0, color=(46, 204, 113))
        physics_engine.add_box("deck_3", 520, 315, 120, 16, mass=10.0, color=(46, 204, 113))
        # Pin joints
        physics_engine.add_pin_joint("j_left", "pier_left", "deck_1", (35, -70), (-60, 0))
        physics_engine.add_pin_joint("j_mid1", "deck_1", "deck_2", (60, 0), (-80, 0))
        physics_engine.add_pin_joint("j_mid2", "deck_2", "deck_3", (80, 0), (-60, 0))
        physics_engine.add_pin_joint("j_right", "deck_3", "pier_right", (60, 0), (-35, -70))
        # Heavy test load dropped from above
        physics_engine.add_circle("impact_load", 380, 120, 28, mass=35.0, color=(231, 76, 60))
        
    elif preset_id == "pendulum_shm":
        # Rigid ceiling anchor
        physics_engine.add_box("ceiling_anchor", 380, 80, 60, 20, static=True, color=(100, 110, 120))
        # Deflected bob position (angle ~ 40 deg, length ~ 220px)
        physics_engine.add_circle("pendulum_bob", 240, 220, 22, mass=6.0, friction=0.05, elasticity=0.8, color=(52, 152, 219))
        physics_engine.add_pin_joint("rod", "ceiling_anchor", "pendulum_bob", (0, 0), (0, 0))

    physics_engine.set_monitored_metrics(preset["metrics"])
    physics_engine.capture_initial_snapshot()
    return preset
