"""
Comprehensive Preset Experiments Library for PROJECT RIA — Research Intelligence Aariz (SDG 9).
Provides 10 verified, demonstration-ready scientific experiments with defined aims,
apparatus setups, theoretical benchmarks, and live telemetry.
"""

from typing import Dict, Any, List
import pymunk

PRESET_EXPERIMENTS: List[Dict[str, Any]] = [
    {
        "id": "galileo_drop",
        "title": "1. Galileo's Free Fall Test (Equivalence Principle)",
        "aim": "Demonstrate that in a gravitational field, acceleration is independent of body mass (10 kg vs 2 kg dropped side-by-side).",
        "theoretical_benchmark": "a1 = a2 = g = 9.00 m/s²; v(t) = g * t",
        "conclusion": "Both spheres impact the floor simultaneously at identical velocities, proving that gravitational acceleration does not depend on mass.",
        "metrics": [
            {"id": "v_heavy", "name": "Heavy Sphere (10kg) v", "target_body": "heavy_sphere", "type": "velocity", "unit": "m/s"},
            {"id": "v_light", "name": "Light Sphere (2kg) v", "target_body": "light_sphere", "type": "velocity", "unit": "m/s"},
            {"id": "h_heavy", "name": "Heavy Sphere Height", "target_body": "heavy_sphere", "type": "height", "unit": "m"},
            {"id": "ke_heavy", "name": "Heavy Sphere Ke", "target_body": "heavy_sphere", "type": "kinetic_energy", "unit": "J"}
        ],
        "setup_function": "load_galileo_drop"
    },
    {
        "id": "incline_friction",
        "title": "2. Incline Friction & Sled Acceleration (Solid Wedge)",
        "aim": "Verify a = g(sin θ - μ cos θ) by measuring acceleration of a wooden block on a 30° solid wedge with friction μ = 0.35.",
        "theoretical_benchmark": "a_theor = 9.0 * (sin 30° - 0.35 * cos 30°) = 1.77 m/s²",
        "conclusion": "Measured acceleration confirms Coulomb friction and normal reaction force Fn = mg cos θ (SDG 9 Sustainable Transport).",
        "metrics": [
            {"id": "theta", "name": "Incline Angle (θ)", "unit": "°", "type": "constant", "value": 30.0},
            {"id": "mu", "name": "Friction Coeff (μ)", "unit": "", "type": "constant", "value": 0.35},
            {"id": "v_block", "name": "Block Velocity (v)", "target_body": "wooden_block", "type": "velocity", "unit": "m/s"},
            {"id": "a_block", "name": "Acceleration (a)", "target_body": "wooden_block", "type": "accel", "unit": "m/s²"}
        ],
        "setup_function": "load_incline_friction"
    },
    {
        "id": "newtons_cradle",
        "title": "3. Newton's Cradle (Kinetic Momentum Transfer Chain)",
        "aim": "Demonstrate elastic collision propagation through a 5-ball pendulum sequence where p = const and E_k = const.",
        "theoretical_benchmark": "Conservation: p_in = p_out; restitution e ≈ 0.98",
        "conclusion": "Impact momentum propagates sequentially through stationary intermediate bobs, ejecting the opposite end with conserved kinetic energy.",
        "metrics": [
            {"id": "v_bob0", "name": "Leading Bob Velocity", "target_body": "bob_0", "type": "velocity", "unit": "m/s"},
            {"id": "v_bob4", "name": "Ejected Bob Velocity", "target_body": "bob_4", "type": "velocity", "unit": "m/s"},
            {"id": "ke_bob4", "name": "Ejected Bob Ke", "target_body": "bob_4", "type": "kinetic_energy", "unit": "J"},
            {"id": "tot_e", "name": "System Mechanical E", "target_body": "bob_4", "type": "total_energy", "unit": "J"}
        ],
        "setup_function": "load_newtons_cradle"
    },
    {
        "id": "elastic_collision",
        "title": "4. 2-Body Elastic Collision & Velocity Exchange",
        "aim": "Demonstrate momentum conservation and kinetic energy exchange between a heavy moving striker (8 kg) and a light stationary target (3 kg).",
        "theoretical_benchmark": "p_initial = m1*v1 = const; v2' = [2*m1 / (m1 + m2)] * v1",
        "conclusion": "Confirms kinetic energy and momentum transfer in industrial milling and collision isolation machinery (SDG 9).",
        "metrics": [
            {"id": "v_striker", "name": "Striker Velocity (v1)", "target_body": "striker_sphere", "type": "velocity", "unit": "m/s"},
            {"id": "v_target", "name": "Target Velocity (v2)", "target_body": "target_sphere", "type": "velocity", "unit": "m/s"},
            {"id": "p_tot", "name": "Total Momentum", "target_body": "striker_sphere", "type": "momentum", "unit": "kg·m/s"},
            {"id": "ke_target", "name": "Target Kinetic Energy", "target_body": "target_sphere", "type": "kinetic_energy", "unit": "J"}
        ],
        "setup_function": "load_elastic_collision"
    },
    {
        "id": "truss_bridge",
        "title": "5. Structural Bridge Deflection (SDG 9 Infrastructure)",
        "aim": "Evaluate bending moment and pinned joint deflection across a 3-segment bridge deck spanning 4.8m under a 35 kg impact load.",
        "theoretical_benchmark": "Static Equilibrium: ΣFy = 0; Reactions R1 = R2 = 0.5 * W_total ≈ 310 N",
        "conclusion": "Pinned joints distribute dynamic shock through deck chords to abutments, preventing bridge span shear collapse (SDG 9).",
        "metrics": [
            {"id": "load_m", "name": "Test Load Mass", "unit": "kg", "type": "constant", "value": 35.0},
            {"id": "v_load", "name": "Load Velocity", "target_body": "impact_load", "type": "velocity", "unit": "m/s"},
            {"id": "ke_load", "name": "Impact Kinetic Energy", "target_body": "impact_load", "type": "kinetic_energy", "unit": "J"},
            {"id": "v_mid", "name": "Mid-Deck Velocity", "target_body": "deck_2", "type": "velocity", "unit": "m/s"}
        ],
        "setup_function": "load_truss_bridge"
    },
    {
        "id": "pendulum_shm",
        "title": "6. Simple Harmonic Motion & Tuned Mass Damping",
        "aim": "Verify that oscillation period T = 2π√(L/g) is governed by effective length and independent of bob mass for small angles.",
        "theoretical_benchmark": "Theoretical Period T = 2π * √(2.2 / 9.0) = 3.10 s",
        "conclusion": "Periodic restoring torque stabilizes structural oscillation. Directly models tuned mass dampers in skyscraper seismic protection (SDG 9 / 11).",
        "metrics": [
            {"id": "v_bob", "name": "Bob Linear Speed", "target_body": "pendulum_bob", "type": "velocity", "unit": "m/s"},
            {"id": "ac_bob", "name": "Centripetal Accel", "target_body": "pendulum_bob", "type": "accel", "unit": "m/s²"},
            {"id": "ke_bob", "name": "Bob Kinetic Energy", "target_body": "pendulum_bob", "type": "kinetic_energy", "unit": "J"},
            {"id": "h_bob", "name": "Bob Height", "target_body": "pendulum_bob", "type": "height", "unit": "m"}
        ],
        "setup_function": "load_pendulum_shm"
    },
    {
        "id": "skid_braking",
        "title": "7. High-Friction Skid & Braking Distance",
        "aim": "Measure deceleration a = -μg and braking distance of a 6 kg crate launched horizontally across a high-friction surface (μ = 0.70).",
        "theoretical_benchmark": "a = -μ * g = -0.70 * 9.0 = -6.30 m/s²; Stopping distance d = v0² / (2μg)",
        "conclusion": "Directly models vehicle braking dynamics and runway friction requirements under wet/dry pavement conditions (SDG 9 Transport Safety).",
        "metrics": [
            {"id": "mu", "name": "Surface Friction (μ)", "unit": "", "type": "constant", "value": 0.70},
            {"id": "v_crate", "name": "Crate Velocity (v)", "target_body": "skid_crate", "type": "velocity", "unit": "m/s"},
            {"id": "a_crate", "name": "Deceleration (a)", "target_body": "skid_crate", "type": "accel", "unit": "m/s²"},
            {"id": "ke_crate", "name": "Kinetic Energy", "target_body": "skid_crate", "type": "kinetic_energy", "unit": "J"}
        ],
        "setup_function": "load_skid_braking"
    },
    {
        "id": "catapult_lever",
        "title": "8. Mechanical Advantage & Lever Arm Catapult",
        "aim": "Demonstrate torque amplification τ = F * d and angular velocity conversion to launch a lightweight projectile ball.",
        "theoretical_benchmark": "Torque Ratio = L_long / L_short; Angular Momentum L = I * ω",
        "conclusion": "Mechanical leverage efficiently converts heavy counterweight torque into high linear exit velocity for material handling.",
        "metrics": [
            {"id": "v_projectile", "name": "Projectile Exit Speed", "target_body": "projectile_ball", "type": "velocity", "unit": "m/s"},
            {"id": "h_projectile", "name": "Projectile Altitude", "target_body": "projectile_ball", "type": "height", "unit": "m"},
            {"id": "ke_projectile", "name": "Exit Kinetic Energy", "target_body": "projectile_ball", "type": "kinetic_energy", "unit": "J"},
            {"id": "v_arm", "name": "Lever Arm Tip Speed", "target_body": "lever_arm", "type": "velocity", "unit": "m/s"}
        ],
        "setup_function": "load_catapult_lever"
    },
    {
        "id": "bouncing_restitution",
        "title": "9. Coefficient of Restitution & Energy Decay",
        "aim": "Measure kinetic energy loss and bounce height decay of an elastic rubber ball (e = 0.85) over repeated ground rebounds.",
        "theoretical_benchmark": "Energy Retention Ratio = e² ≈ 0.72 per rebound; Peak Height h_n = h0 * e^(2n)",
        "conclusion": "Inelastic restitution dissipates mechanical energy into thermal and sonic waves, validating vibration dampers (SDG 9).",
        "metrics": [
            {"id": "v_ball", "name": "Ball Velocity (v)", "target_body": "rebound_ball", "type": "velocity", "unit": "m/s"},
            {"id": "h_ball", "name": "Bounce Altitude", "target_body": "rebound_ball", "type": "height", "unit": "m"},
            {"id": "ke_ball", "name": "Kinetic Energy", "target_body": "rebound_ball", "type": "kinetic_energy", "unit": "J"},
            {"id": "tot_energy", "name": "Mechanical Energy", "target_body": "rebound_ball", "type": "total_energy", "unit": "J"}
        ],
        "setup_function": "load_bouncing_restitution"
    },
    {
        "id": "wrecking_ball",
        "title": "10. Wrecking Ball & Structural Impact Demolition",
        "aim": "Demonstrate kinetic momentum impact of a 15 kg pendulum mass striking a multi-tier structural block tower.",
        "theoretical_benchmark": "Impact Energy E_k = 0.5 * m * v_impact²; Impulse J = Δp",
        "conclusion": "Dynamic impact overcomes static structural friction thresholds, inducing progressive collapse of unreinforced block masonry.",
        "metrics": [
            {"id": "v_ball", "name": "Wrecking Ball Speed", "target_body": "wrecking_ball", "type": "velocity", "unit": "m/s"},
            {"id": "ke_ball", "name": "Impact Kinetic Energy", "target_body": "wrecking_ball", "type": "kinetic_energy", "unit": "J"},
            {"id": "v_top_block", "name": "Top Block Velocity", "target_body": "block_top", "type": "velocity", "unit": "m/s"},
            {"id": "v_mid_block", "name": "Mid Block Velocity", "target_body": "block_mid", "type": "velocity", "unit": "m/s"}
        ],
        "setup_function": "load_wrecking_ball"
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
    
    if preset_id == "galileo_drop":
        # Two spheres side-by-side at y=100
        physics_engine.add_circle("heavy_sphere", 280, 100, 26, mass=10.0, friction=0.3, elasticity=0.2, color=(37, 99, 235))
        physics_engine.add_circle("light_sphere", 480, 100, 16, mass=2.0, friction=0.3, elasticity=0.2, color=(16, 185, 129))

    elif preset_id == "incline_friction":
        physics_engine.add_wedge("solid_wedge", 80, 520, 254.0, friction=0.35, elasticity=0.2)
        physics_engine.add_box("wooden_block", 0, 0, 42, 28, mass=6.0, friction=0.35, elasticity=0.1, color=(217, 119, 6), on_wedge="solid_wedge")
        
    elif preset_id == "newtons_cradle":
        y_pivot = 80
        spacing = 38
        r = 18
        for i in range(5):
            name = f"bob_{i}"
            x = 300 + i * spacing
            physics_engine.add_circle(name, x, y_pivot + 180, r, mass=4.0, elasticity=0.98, friction=0.05, color=(37, 99, 235))
            anchor = pymunk.Body(body_type=pymunk.Body.STATIC)
            anchor.position = (x, y_pivot)
            physics_engine.space.add(anchor)
            joint = pymunk.PinJoint(anchor, physics_engine.named_bodies[name], (0, 0), (0, 0))
            physics_engine.space.add(joint)
        # Pull back bob 0
        physics_engine.apply_impulse("bob_0", (-1200, -300))

    elif preset_id == "elastic_collision":
        physics_engine.add_segment("runway", 40, 440, 720, 440, thickness=10, friction=0.05, elasticity=0.98)
        physics_engine.add_circle("striker_sphere", 140, 415, 25, mass=8.0, friction=0.05, elasticity=0.98, color=(16, 185, 129))
        physics_engine.add_circle("target_sphere", 380, 422, 18, mass=3.0, friction=0.05, elasticity=0.98, color=(37, 99, 235))
        physics_engine.apply_impulse("striker_sphere", (3200, 0))
        
    elif preset_id == "truss_bridge":
        physics_engine.add_box("pier_left", 140, 380, 70, 140, static=True, color=(100, 116, 139))
        physics_engine.add_box("pier_right", 620, 380, 70, 140, static=True, color=(100, 116, 139))
        physics_engine.add_box("deck_1", 240, 315, 120, 16, mass=10.0, color=(16, 185, 129))
        physics_engine.add_box("deck_2", 380, 315, 160, 16, mass=14.0, color=(16, 185, 129))
        physics_engine.add_box("deck_3", 520, 315, 120, 16, mass=10.0, color=(16, 185, 129))
        physics_engine.add_pin_joint("j_left", "pier_left", "deck_1", (35, -70), (-60, 0))
        physics_engine.add_pin_joint("j_mid1", "deck_1", "deck_2", (60, 0), (-80, 0))
        physics_engine.add_pin_joint("j_mid2", "deck_2", "deck_3", (80, 0), (-60, 0))
        physics_engine.add_pin_joint("j_right", "deck_3", "pier_right", (60, 0), (-35, -70))
        physics_engine.add_circle("impact_load", 380, 110, 28, mass=35.0, color=(220, 38, 38))
        
    elif preset_id == "pendulum_shm":
        physics_engine.add_box("ceiling_anchor", 380, 70, 60, 20, static=True, color=(100, 116, 139))
        physics_engine.add_circle("pendulum_bob", 240, 210, 24, mass=6.0, friction=0.05, elasticity=0.8, color=(37, 99, 235))
        physics_engine.add_pin_joint("rod", "ceiling_anchor", "pendulum_bob", (0, 0), (0, 0))

    elif preset_id == "skid_braking":
        physics_engine.add_segment("floor_track", 30, 440, 730, 440, thickness=12, friction=0.70, elasticity=0.1)
        physics_engine.add_box("skid_crate", 100, 415, 45, 35, mass=6.0, friction=0.70, elasticity=0.1, color=(217, 119, 6))
        physics_engine.apply_impulse("skid_crate", (4500, 0))

    elif preset_id == "catapult_lever":
        # Fulcrum
        physics_engine.add_wedge("fulcrum", 340, 420, 60, friction=0.8, color=(100, 116, 139))
        # Long lever beam
        physics_engine.add_box("lever_arm", 380, 395, 340, 16, mass=12.0, friction=0.4, color=(217, 119, 6))
        physics_engine.add_pin_joint("pivot", "fulcrum", "lever_arm", (0, -30), (0, 0))
        # Projectile on right tip
        physics_engine.add_circle("projectile_ball", 530, 375, 14, mass=1.5, friction=0.3, elasticity=0.8, color=(220, 38, 38))
        # Counterweight drop on left arm
        physics_engine.add_box("counterweight", 230, 150, 50, 50, mass=30.0, friction=0.5, color=(37, 99, 235))

    elif preset_id == "bouncing_restitution":
        physics_engine.add_circle("rebound_ball", 380, 90, 22, mass=4.0, friction=0.2, elasticity=0.88, color=(16, 185, 129))

    elif preset_id == "wrecking_ball":
        # 3-tier tower
        physics_engine.add_box("block_base", 560, 425, 40, 35, mass=8.0, friction=0.6, color=(217, 119, 6))
        physics_engine.add_box("block_mid", 560, 385, 40, 35, mass=6.0, friction=0.6, color=(217, 119, 6))
        physics_engine.add_box("block_top", 560, 345, 40, 35, mass=4.0, friction=0.6, color=(217, 119, 6))
        # Wrecking ball suspended on left
        physics_engine.add_box("anchor_beam", 200, 80, 60, 20, static=True, color=(100, 116, 139))
        physics_engine.add_circle("wrecking_ball", 120, 240, 28, mass=18.0, friction=0.2, elasticity=0.85, color=(37, 99, 235))
        physics_engine.add_pin_joint("cable", "anchor_beam", "wrecking_ball", (0, 0), (0, 0))
        physics_engine.apply_impulse("wrecking_ball", (2500, 0))

    physics_engine.set_monitored_metrics(preset["metrics"])
    physics_engine.capture_initial_snapshot()
    return preset
