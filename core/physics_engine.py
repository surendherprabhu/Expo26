"""
Physics Engine Module for Universal AI Simulation Environment.
Uses Pymunk (Chipmunk2D) to simulate 2D rigid-body dynamics, triangular wedges, 
constraints, dynamic scientific telemetry with fuzzy body resolution, and automatic metrics.
"""

import math
import pymunk
from typing import Dict, List, Optional, Tuple, Any

class PhysicsEngine:
    def __init__(self, width: int = 760, height: int = 480):
        self.width = width
        self.height = height
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)  # Standard downward gravity (~9.0 m/s^2 scaled)
        self.space.damping = 0.999      # Slight air resistance
        
        # Registry of named bodies, shapes, and joints
        self.named_bodies: Dict[str, pymunk.Body] = {}
        self.named_shapes: Dict[str, pymunk.Shape] = {}
        self.named_joints: Dict[str, pymunk.Constraint] = {}
        self.colors: Dict[str, Tuple[int, int, int]] = {}
        
        # Geometry metadata for wedges / ramps
        self.wedge_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Initial snapshot for resetting to t=0
        self.initial_snapshot: Optional[Dict[str, Any]] = None
        
        # Experiment tracking & data logging
        self.experiment_metadata: Dict[str, Any] = {
            "title": "General Mechanics Simulation",
            "aim": "Observe physical interaction of rigid bodies.",
            "theoretical_benchmark": "N/A"
        }
        self.peak_velocity = 0.0
        self.velocity_samples: List[float] = []
        self.experiment_active = False
        
        # Velocity history for acceleration calculations
        self._prev_velocities: Dict[str, Tuple[float, float]] = {}
        self._current_accelerations: Dict[str, float] = {}
        
        # Dynamic Experiment Variables defined by AI or presets
        self.monitored_metrics: List[Dict[str, Any]] = []
        
        # Telemetry history
        self.total_sim_time = 0.0
        self.step_dt = 1.0 / 60.0
        self.paused = True  # Always paused on setup!
        
        # Build default boundary walls
        self._create_boundaries()

    def _create_boundaries(self, thickness: float = 20.0):
        """Creates static boundary walls along bottom, left, and right."""
        w = float(self.width)
        h = float(self.height)
        
        floor = pymunk.Segment(self.space.static_body, (0, h - thickness), (w, h - thickness), thickness)
        floor.elasticity = 0.5
        floor.friction = 0.8
        floor.color = (51, 65, 85, 255)  # Sturdy dark slate lab bench
        
        left_wall = pymunk.Segment(self.space.static_body, (thickness, 0), (thickness, h), thickness)
        left_wall.elasticity = 0.5
        left_wall.friction = 0.5
        left_wall.color = (51, 65, 85, 255)
        
        right_wall = pymunk.Segment(self.space.static_body, (w - thickness, 0), (w - thickness, h), thickness)
        right_wall.elasticity = 0.5
        right_wall.friction = 0.5
        right_wall.color = (51, 65, 85, 255)
        
        self.space.add(floor, left_wall, right_wall)
        self.named_shapes["boundary_floor"] = floor
        self.named_shapes["boundary_left"] = left_wall
        self.named_shapes["boundary_right"] = right_wall

    def reset(self):
        """Completely clears all objects and resets the environment."""
        for constraint in list(self.space.constraints):
            self.space.remove(constraint)
        for shape in list(self.space.shapes):
            self.space.remove(shape)
        for body in list(self.space.bodies):
            if body != self.space.static_body:
                self.space.remove(body)
                
        self.named_bodies.clear()
        self.named_shapes.clear()
        self.named_joints.clear()
        self.colors.clear()
        self.wedge_metadata.clear()
        self._prev_velocities.clear()
        self._current_accelerations.clear()
        self.monitored_metrics.clear()
        self.velocity_samples.clear()
        self.initial_snapshot = None
        self.total_sim_time = 0.0
        self.peak_velocity = 0.0
        self.paused = True
        self.experiment_active = False
        self.space.gravity = (0, 900)
        self._create_boundaries()

    def capture_initial_snapshot(self):
        """Saves initial state of dynamic bodies so the experiment can be reset to t=0."""
        snapshot = {}
        for name, body in self.named_bodies.items():
            if body.body_type == pymunk.Body.DYNAMIC:
                snapshot[name] = {
                    "pos": (body.position.x, body.position.y),
                    "angle": body.angle,
                    "vel": (body.velocity.x, body.velocity.y),
                    "ang_vel": body.angular_velocity
                }
        self.initial_snapshot = snapshot
        self.total_sim_time = 0.0
        self.peak_velocity = 0.0
        self.velocity_samples.clear()
        self.paused = True

    def reset_to_initial_state(self):
        """Restores bodies to t=0 positions without clearing the apparatus."""
        if not self.initial_snapshot:
            return
        for name, state in self.initial_snapshot.items():
            if name in self.named_bodies:
                body = self.named_bodies[name]
                body.position = state["pos"]
                body.angle = state["angle"]
                body.velocity = (0, 0)
                body.angular_velocity = 0.0
        self.total_sim_time = 0.0
        self.peak_velocity = 0.0
        self.velocity_samples.clear()
        self.paused = True

    def set_monitored_metrics(self, metrics: List[Dict[str, Any]]):
        """Sets the dynamic experiment variables."""
        self.monitored_metrics = metrics

    def add_wedge(
        self,
        name: str,
        x_left: float,
        x_right: float,
        height: float,
        friction: float = 0.5,
        elasticity: float = 0.2,
        color: Tuple[int, int, int] = (100, 116, 139)
    ) -> bool:
        """
        Creates a solid triangular incline wedge resting flat on the ground floor.
        """
        try:
            floor_y = self.height - 20.0
            top_y = floor_y - height
            
            verts = [
                (x_left, floor_y),
                (x_right, floor_y),
                (x_left, top_y)
            ]
            
            shape = pymunk.Poly(self.space.static_body, verts)
            shape.friction = friction
            shape.elasticity = elasticity
            shape.color = (*color, 255)
            self.space.add(shape)
            
            self.named_shapes[name] = shape
            self.colors[name] = color
            
            angle_rad = math.atan2(height, x_right - x_left)
            self.wedge_metadata[name] = {
                "x_left": x_left,
                "x_right": x_right,
                "floor_y": floor_y,
                "top_y": top_y,
                "height": height,
                "angle_rad": angle_rad,
                "angle_deg": math.degrees(angle_rad),
                "friction": friction
            }
            return True
        except Exception as e:
            print(f"Error creating wedge '{name}': {e}")
            return False

    def add_box(
        self,
        name: str,
        x: float,
        y: float,
        width: float,
        height: float,
        mass: float = 5.0,
        elasticity: float = 0.6,
        friction: float = 0.7,
        static: bool = False,
        color: Tuple[int, int, int] = (217, 119, 6),
        on_wedge: Optional[str] = None
    ) -> bool:
        """Creates a rectangular rigid body. If on_wedge is set, snaps onto wedge slope."""
        try:
            body_angle = 0.0
            if on_wedge and on_wedge in self.wedge_metadata:
                w_meta = self.wedge_metadata[on_wedge]
                body_angle = w_meta["angle_rad"]
                dist_down_slope = width * 1.2
                x = w_meta["x_left"] + math.cos(body_angle) * dist_down_slope
                y = w_meta["top_y"] + math.sin(body_angle) * dist_down_slope - (height / 2.0)

            if static or mass <= 0:
                body = pymunk.Body(body_type=pymunk.Body.STATIC)
                body.position = (x, y)
                body.angle = body_angle
                shape = pymunk.Poly.create_box(body, (width, height))
            else:
                moment = pymunk.moment_for_box(mass, (width, height))
                body = pymunk.Body(mass, moment)
                body.position = (x, y)
                body.angle = body_angle
                shape = pymunk.Poly.create_box(body, (width, height))
            
            shape.elasticity = max(0.0, min(1.0, elasticity))
            shape.friction = max(0.0, friction)
            shape.color = (*color, 255)
            
            self.space.add(body, shape)
                
            self.named_bodies[name] = body
            self.named_shapes[name] = shape
            self.colors[name] = color
            return True
        except Exception as e:
            print(f"Error adding box '{name}': {e}")
            return False

    def add_circle(
        self,
        name: str,
        x: float,
        y: float,
        radius: float,
        mass: float = 3.0,
        elasticity: float = 0.8,
        friction: float = 0.5,
        static: bool = False,
        color: Tuple[int, int, int] = (37, 99, 235),
        on_wedge: Optional[str] = None
    ) -> bool:
        """Creates a circular rigid body. If on_wedge is set, snaps onto wedge slope."""
        try:
            if on_wedge and on_wedge in self.wedge_metadata:
                w_meta = self.wedge_metadata[on_wedge]
                body_angle = w_meta["angle_rad"]
                dist_down_slope = radius * 2.0
                x = w_meta["x_left"] + math.cos(body_angle) * dist_down_slope
                y = w_meta["top_y"] + math.sin(body_angle) * dist_down_slope - radius

            if static or mass <= 0:
                body = pymunk.Body(body_type=pymunk.Body.STATIC)
                body.position = (x, y)
                shape = pymunk.Circle(body, radius)
            else:
                moment = pymunk.moment_for_circle(mass, 0, radius)
                body = pymunk.Body(mass, moment)
                body.position = (x, y)
                shape = pymunk.Circle(body, radius)
                
            shape.elasticity = max(0.0, min(1.0, elasticity))
            shape.friction = max(0.0, friction)
            shape.color = (*color, 255)
            
            self.space.add(body, shape)
                
            self.named_bodies[name] = body
            self.named_shapes[name] = shape
            self.colors[name] = color
            return True
        except Exception as e:
            print(f"Error adding circle '{name}': {e}")
            return False

    def add_segment(
        self,
        name: str,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        thickness: float = 6.0,
        elasticity: float = 0.5,
        friction: float = 0.6,
        color: Tuple[int, int, int] = (100, 116, 139)
    ) -> bool:
        """Creates a static line segment."""
        try:
            shape = pymunk.Segment(self.space.static_body, (x1, y1), (x2, y2), thickness)
            shape.elasticity = elasticity
            shape.friction = friction
            shape.color = (*color, 255)
            self.space.add(shape)
            self.named_shapes[name] = shape
            self.colors[name] = color
            return True
        except Exception as e:
            print(f"Error adding segment '{name}': {e}")
            return False

    def add_pin_joint(
        self,
        joint_name: str,
        body_a_name: str,
        body_b_name: str,
        anchor_a: Tuple[float, float] = (0, 0),
        anchor_b: Tuple[float, float] = (0, 0)
    ) -> bool:
        """Connects two bodies with a pin joint."""
        try:
            body_a = self.named_bodies.get(body_a_name, self.space.static_body if body_a_name == "world" else None)
            body_b = self.named_bodies.get(body_b_name, self.space.static_body if body_b_name == "world" else None)
            
            if not body_a or not body_b:
                return False
                
            joint = pymunk.PinJoint(body_a, body_b, anchor_a, anchor_b)
            self.space.add(joint)
            self.named_joints[joint_name] = joint
            return True
        except Exception as e:
            print(f"Error adding pin joint '{joint_name}': {e}")
            return False

    def apply_impulse(self, body_name: str, impulse: Tuple[float, float]) -> bool:
        """Applies an impulse force with fuzzy body resolution."""
        body = self._resolve_body(body_name)
        if body and body.body_type == pymunk.Body.DYNAMIC:
            body.apply_impulse_at_local_point(impulse)
            return True
        return False

    def set_gravity(self, gx: float, gy: float):
        """Sets world gravity."""
        self.space.gravity = (gx, gy)

    def step(self, dt: Optional[float] = None) -> None:
        """Advances physics step and records telemetry samples."""
        if self.paused:
            return
        actual_dt = dt or self.step_dt
        
        # Track velocity & acceleration
        for name, body in self.named_bodies.items():
            if body.body_type == pymunk.Body.DYNAMIC:
                v_current = body.velocity.length
                prev_v, _ = self._prev_velocities.get(name, (v_current, self.total_sim_time))
                accel = (v_current - prev_v) / max(0.0001, actual_dt)
                self._current_accelerations[name] = accel / 100.0
                self._prev_velocities[name] = (v_current, self.total_sim_time)
                
                v_mps = v_current / 100.0
                if v_mps > self.peak_velocity:
                    self.peak_velocity = v_mps
                self.velocity_samples.append(v_mps)
                
        self.space.step(actual_dt)
        self.total_sim_time += actual_dt

    def _resolve_body(self, target_name: str) -> Optional[pymunk.Body]:
        """Fuzzy target body resolution to prevent '--' when the AI passes slightly mismatched names."""
        if not target_name:
            # Return first dynamic body if target_name is omitted
            for b in self.named_bodies.values():
                if b.body_type == pymunk.Body.DYNAMIC:
                    return b
            return None

        # 1. Direct match
        if target_name in self.named_bodies:
            return self.named_bodies[target_name]

        # 2. Case-insensitive match
        t_lower = target_name.lower().replace(" ", "_")
        for name, b in self.named_bodies.items():
            if name.lower() == t_lower:
                return b

        # 3. Substring match
        for name, b in self.named_bodies.items():
            if t_lower in name.lower() or name.lower() in t_lower:
                return b

        # 4. Fallback: first dynamic body
        for b in self.named_bodies.values():
            if b.body_type == pymunk.Body.DYNAMIC:
                return b

        return None

    def get_dynamic_telemetry(self) -> Dict[str, Any]:
        """
        Evaluates model-defined variables live at 60 FPS with robust type support
        and automatic metric fallback if none are provided.
        """
        g = abs(self.space.gravity[1]) / 100.0
        ground_y = self.height - 20.0
        dynamic_bodies = {n: b for n, b in self.named_bodies.items() if b.body_type == pymunk.Body.DYNAMIC}
        
        # If no metrics were configured, automatically generate clean live telemetry for active bodies
        active_metrics = self.monitored_metrics
        if not active_metrics and dynamic_bodies:
            active_metrics = []
            for b_name in list(dynamic_bodies.keys())[:3]:
                clean_name = b_name.replace("_", " ").title()
                active_metrics.extend([
                    {"id": f"v_{b_name}", "name": f"{clean_name} Velocity", "unit": "m/s", "type": "velocity", "target_body": b_name},
                    {"id": f"h_{b_name}", "name": f"{clean_name} Height", "unit": "m", "type": "height", "target_body": b_name},
                    {"id": f"ke_{b_name}", "name": f"{clean_name} Kinetic E.", "unit": "J", "type": "kinetic_energy", "target_body": b_name}
                ])
                if len(active_metrics) >= 4:
                    break

        measured_items = []
        for metric in active_metrics:
            m_id = metric.get("id", "var")
            name = metric.get("name", m_id)
            unit = metric.get("unit", "")
            m_type = str(metric.get("type", "constant")).lower()
            target = metric.get("target_body", "")
            val_display = "--"

            body = self._resolve_body(target)

            if m_type in ["constant", "param"]:
                val = metric.get("value", 0.0)
                val_display = f"{val:.2f}" if isinstance(val, (int, float)) else str(val)

            elif m_type in ["velocity", "speed"]:
                if body and body.body_type == pymunk.Body.DYNAMIC:
                    val_display = f"{(body.velocity.length / 100.0):.2f}"

            elif m_type in ["accel", "acceleration"]:
                # Lookup acceleration of resolved body
                acc = 0.0
                if body:
                    for bname, bobj in self.named_bodies.items():
                        if bobj == body:
                            acc = self._current_accelerations.get(bname, 0.0)
                            break
                val_display = f"{acc:.2f}"

            elif m_type in ["height", "altitude", "position_y"]:
                if body:
                    h_m = max(0.0, (ground_y - body.position.y) / 100.0)
                    val_display = f"{h_m:.2f}"

            elif m_type in ["kinetic_energy", "ke"]:
                if body and body.body_type == pymunk.Body.DYNAMIC:
                    v = body.velocity.length / 100.0
                    ke = 0.5 * body.mass * (v ** 2)
                    val_display = f"{ke:.2f}"

            elif m_type in ["potential_energy", "pe"]:
                if body and body.body_type == pymunk.Body.DYNAMIC:
                    h_m = max(0.0, (ground_y - body.position.y) / 100.0)
                    pe = body.mass * g * h_m
                    val_display = f"{pe:.2f}"

            elif m_type in ["total_energy", "mechanical_energy"]:
                if body and body.body_type == pymunk.Body.DYNAMIC:
                    v = body.velocity.length / 100.0
                    h_m = max(0.0, (ground_y - body.position.y) / 100.0)
                    tot = (0.5 * body.mass * (v ** 2)) + (body.mass * g * h_m)
                    val_display = f"{tot:.2f}"

            elif m_type in ["momentum"]:
                if body and body.body_type == pymunk.Body.DYNAMIC:
                    p = body.mass * (body.velocity.length / 100.0)
                    val_display = f"{p:.2f}"

            elif m_type in ["normal_force"]:
                if body and body.body_type == pymunk.Body.DYNAMIC:
                    angle_deg = metric.get("value", 30.0)
                    fn = body.mass * g * math.cos(math.radians(angle_deg))
                    val_display = f"{fn:.2f}"

            elif m_type in ["mass"]:
                if body:
                    val_display = f"{body.mass:.2f}"

            measured_items.append({
                "id": m_id,
                "name": name,
                "value": val_display,
                "unit": unit
            })

        return {
            "metrics": measured_items,
            "sim_time": round(self.total_sim_time, 2),
            "is_paused": self.paused
        }

    def generate_experiment_report(self) -> Dict[str, Any]:
        """
        Generates the formal Experiment Control Sheet / Report summarizing
        the completed run for the bottom-right panel.
        """
        avg_v = sum(self.velocity_samples) / max(1, len(self.velocity_samples))
        
        return {
            "title": self.experiment_metadata.get("title", "Physics Experimentation Run"),
            "aim": self.experiment_metadata.get("aim", "Investigate mechanical response."),
            "theoretical_benchmark": self.experiment_metadata.get("theoretical_benchmark", "N/A"),
            "duration_sec": round(self.total_sim_time, 2),
            "peak_velocity_mps": round(self.peak_velocity, 2),
            "avg_velocity_mps": round(avg_v, 2),
            "active_bodies": len([b for b in self.space.bodies if b.body_type == pymunk.Body.DYNAMIC]),
            "conclusion": self.experiment_metadata.get("conclusion", "Experiment completed. Data recorded.")
        }
