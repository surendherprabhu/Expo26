"""
Physics Engine Module for Universal AI Simulation Environment.
Uses Pymunk (Chipmunk2D) to simulate 2D rigid-body dynamics, constraints, and dynamic scientific telemetry.
"""

import math
import pymunk
from typing import Dict, List, Optional, Tuple, Any

class PhysicsEngine:
    def __init__(self, width: int = 760, height: int = 480):
        self.width = width
        self.height = height
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)  # Standard downward gravity
        self.space.damping = 0.999      # Slight air resistance
        
        # Registry of named bodies, shapes, and joints
        self.named_bodies: Dict[str, pymunk.Body] = {}
        self.named_shapes: Dict[str, pymunk.Shape] = {}
        self.named_joints: Dict[str, pymunk.Constraint] = {}
        self.colors: Dict[str, Tuple[int, int, int]] = {}
        
        # Velocity history for acceleration calculations: {body_name: (last_v, last_time)}
        self._prev_velocities: Dict[str, Tuple[float, float]] = {}
        self._current_accelerations: Dict[str, float] = {}
        
        # Dynamic Experiment Variables defined by the AI model
        self.monitored_metrics: List[Dict[str, Any]] = []
        
        # Telemetry history
        self.total_sim_time = 0.0
        self.step_dt = 1.0 / 60.0
        self.paused = False
        
        # Build default boundary walls
        self._create_boundaries()

    def _create_boundaries(self, thickness: float = 20.0):
        """Creates static boundary walls along bottom, left, and right."""
        w = float(self.width)
        h = float(self.height)
        
        floor = pymunk.Segment(self.space.static_body, (0, h - thickness), (w, h - thickness), thickness)
        floor.elasticity = 0.5
        floor.friction = 0.8
        floor.color = (60, 65, 75, 255)
        
        left_wall = pymunk.Segment(self.space.static_body, (thickness, 0), (thickness, h), thickness)
        left_wall.elasticity = 0.5
        left_wall.friction = 0.5
        left_wall.color = (60, 65, 75, 255)
        
        right_wall = pymunk.Segment(self.space.static_body, (w - thickness, 0), (w - thickness, h), thickness)
        right_wall.elasticity = 0.5
        right_wall.friction = 0.5
        right_wall.color = (60, 65, 75, 255)
        
        self.space.add(floor, left_wall, right_wall)
        self.named_shapes["boundary_floor"] = floor
        self.named_shapes["boundary_left"] = left_wall
        self.named_shapes["boundary_right"] = right_wall

    def reset(self):
        """Clears all objects and re-initializes boundaries."""
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
        self._prev_velocities.clear()
        self._current_accelerations.clear()
        self.monitored_metrics.clear()
        self.total_sim_time = 0.0
        self.space.gravity = (0, 900)
        self._create_boundaries()

    def set_monitored_metrics(self, metrics: List[Dict[str, Any]]):
        """Sets the dynamic experiment variables defined by the AI."""
        self.monitored_metrics = metrics

    def step(self, dt: Optional[float] = None) -> None:
        """Advances simulation by dt if not paused, updating accelerations."""
        if self.paused:
            return
        actual_dt = dt or self.step_dt
        
        # Track velocities before step to compute acceleration
        for name, body in self.named_bodies.items():
            if body.body_type == pymunk.Body.DYNAMIC:
                v_current = body.velocity.length
                prev_v, _ = self._prev_velocities.get(name, (v_current, self.total_sim_time))
                accel = (v_current - prev_v) / max(0.0001, actual_dt)
                # Convert from pixels/s^2 to m/s^2 (100 px = 1 m)
                self._current_accelerations[name] = accel / 100.0
                self._prev_velocities[name] = (v_current, self.total_sim_time)
                
        self.space.step(actual_dt)
        self.total_sim_time += actual_dt

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
        color: Tuple[int, int, int] = (46, 204, 113)
    ) -> bool:
        """Creates a rectangular rigid body."""
        try:
            if static or mass <= 0:
                body = pymunk.Body(body_type=pymunk.Body.STATIC)
                body.position = (x, y)
                shape = pymunk.Poly.create_box(body, (width, height))
            else:
                moment = pymunk.moment_for_box(mass, (width, height))
                body = pymunk.Body(mass, moment)
                body.position = (x, y)
                shape = pymunk.Poly.create_box(body, (width, height))
            
            shape.elasticity = max(0.0, min(1.0, elasticity))
            shape.friction = max(0.0, friction)
            shape.color = (*color, 255)
            
            if static or mass <= 0:
                self.space.add(shape)
            else:
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
        color: Tuple[int, int, int] = (52, 152, 219)
    ) -> bool:
        """Creates a circular rigid body."""
        try:
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
            
            if static or mass <= 0:
                self.space.add(shape)
            else:
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
        color: Tuple[int, int, int] = (149, 165, 166)
    ) -> bool:
        """Creates a static line segment (ramps, inclined planes, shelves)."""
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
        """Connects two bodies with a pin joint (hinge / pivot)."""
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

    def add_spring_joint(
        self,
        joint_name: str,
        body_a_name: str,
        body_b_name: str,
        rest_length: float,
        stiffness: float = 100.0,
        damping: float = 5.0,
        anchor_a: Tuple[float, float] = (0, 0),
        anchor_b: Tuple[float, float] = (0, 0)
    ) -> bool:
        """Connects two bodies with a damped spring."""
        try:
            body_a = self.named_bodies.get(body_a_name, self.space.static_body if body_a_name == "world" else None)
            body_b = self.named_bodies.get(body_b_name, self.space.static_body if body_b_name == "world" else None)
            
            if not body_a or not body_b:
                return False
                
            spring = pymunk.DampedSpring(body_a, body_b, anchor_a, anchor_b, rest_length, stiffness, damping)
            self.space.add(spring)
            self.named_joints[joint_name] = spring
            return True
        except Exception as e:
            print(f"Error adding spring joint '{joint_name}': {e}")
            return False

    def apply_impulse(self, body_name: str, impulse: Tuple[float, float]) -> bool:
        """Applies an instantaneous impulse vector (fx, fy) to a body."""
        body = self.named_bodies.get(body_name)
        if body and body.body_type == pymunk.Body.DYNAMIC:
            body.apply_impulse_at_local_point(impulse)
            return True
        return False

    def set_gravity(self, gx: float, gy: float):
        """Sets world gravity vector."""
        self.space.gravity = (gx, gy)

    def get_dynamic_telemetry(self) -> Dict[str, Any]:
        """
        Evaluates and returns the actual variables returned by the AI model,
        measuring what is actually occurring on screen.
        """
        measured_items = []
        g = abs(self.space.gravity[1]) / 100.0  # scaled m/s^2 (approx 9.0 m/s^2)
        ground_y = self.height - 20.0
        
        for metric in self.monitored_metrics:
            m_id = metric.get("id", "var")
            name = metric.get("name", m_id)
            unit = metric.get("unit", "")
            m_type = metric.get("type", "constant")
            target = metric.get("target_body", "")
            val_display = "--"

            if m_type == "constant":
                val = metric.get("value", 0.0)
                val_display = f"{val:.2f}" if isinstance(val, (int, float)) else str(val)

            elif m_type == "velocity":
                body = self.named_bodies.get(target)
                if body and body.body_type == pymunk.Body.DYNAMIC:
                    v_mps = body.velocity.length / 100.0
                    val_display = f"{v_mps:.2f}"

            elif m_type == "accel":
                acc = self._current_accelerations.get(target, 0.0)
                val_display = f"{acc:.2f}"

            elif m_type == "mass":
                body = self.named_bodies.get(target)
                if body:
                    val_display = f"{body.mass:.2f}"

            elif m_type == "friction":
                shape = self.named_shapes.get(target)
                if shape:
                    val_display = f"{shape.friction:.2f}"

            elif m_type == "angle":
                shape = self.named_shapes.get(target)
                if shape and isinstance(shape, pymunk.Segment):
                    dx = shape.b.x - shape.a.x
                    dy = shape.b.y - shape.a.y
                    deg = abs(math.degrees(math.atan2(dy, dx)))
                    val_display = f"{deg:.1f}"
                else:
                    body = self.named_bodies.get(target)
                    if body:
                        deg = math.degrees(body.angle) % 360
                        val_display = f"{deg:.1f}"

            elif m_type == "kinetic_energy":
                body = self.named_bodies.get(target)
                if body and body.body_type == pymunk.Body.DYNAMIC:
                    v = body.velocity.length / 100.0
                    ke = 0.5 * body.mass * (v ** 2)
                    val_display = f"{ke:.2f}"

            elif m_type == "potential_energy":
                body = self.named_bodies.get(target)
                if body and body.body_type == pymunk.Body.DYNAMIC:
                    h_m = max(0.0, (ground_y - body.position.y) / 100.0)
                    pe = body.mass * g * h_m
                    val_display = f"{pe:.2f}"

            elif m_type == "normal_force":
                body = self.named_bodies.get(target)
                angle_deg = metric.get("value", 30.0)
                if body and body.body_type == pymunk.Body.DYNAMIC:
                    fn = body.mass * g * math.cos(math.radians(angle_deg))
                    val_display = f"{fn:.2f}"

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
