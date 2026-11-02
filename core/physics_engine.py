"""
Physics Engine Module for Universal AI Simulation Environment.
Uses Pymunk (Chipmunk2D) to simulate 2D rigid-body dynamics, constraints, and energy calculations.
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
        
        # Registry of named bodies and shapes for conversational referencing
        self.named_bodies: Dict[str, pymunk.Body] = {}
        self.named_shapes: Dict[str, pymunk.Shape] = {}
        self.named_joints: Dict[str, pymunk.Constraint] = {}
        self.colors: Dict[str, Tuple[int, int, int]] = {}
        
        # Telemetry history
        self.total_sim_time = 0.0
        self.step_dt = 1.0 / 60.0
        self.paused = False
        
        # Build default boundary walls so objects don't fall off screen
        self._create_boundaries()

    def _create_boundaries(self, thickness: float = 20.0):
        """Creates static boundary walls along bottom, left, and right."""
        w = float(self.width)
        h = float(self.height)
        
        # Floor
        floor = pymunk.Segment(self.space.static_body, (0, h - thickness), (w, h - thickness), thickness)
        floor.elasticity = 0.5
        floor.friction = 0.8
        floor.color = (60, 65, 75, 255)
        
        # Left wall
        left_wall = pymunk.Segment(self.space.static_body, (thickness, 0), (thickness, h), thickness)
        left_wall.elasticity = 0.5
        left_wall.friction = 0.5
        left_wall.color = (60, 65, 75, 255)
        
        # Right wall
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
        # Remove all constraints
        for constraint in list(self.space.constraints):
            self.space.remove(constraint)
        # Remove all shapes
        for shape in list(self.space.shapes):
            self.space.remove(shape)
        # Remove all non-static bodies
        for body in list(self.space.bodies):
            if body != self.space.static_body:
                self.space.remove(body)
                
        self.named_bodies.clear()
        self.named_shapes.clear()
        self.named_joints.clear()
        self.colors.clear()
        self.total_sim_time = 0.0
        self.space.gravity = (0, 900)
        self._create_boundaries()

    def step(self, dt: Optional[float] = None) -> None:
        """Advances simulation by dt if not paused."""
        if self.paused:
            return
        actual_dt = dt or self.step_dt
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
        color: Tuple[int, int, int] = (46, 204, 113) # Default emerald green
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
        color: Tuple[int, int, int] = (52, 152, 219) # Default blue
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
        color: Tuple[int, int, int] = (149, 165, 166) # Grey
    ) -> bool:
        """Creates a static line segment (ramps, shelves, incline planes)."""
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

    def get_telemetry(self) -> Dict[str, Any]:
        """Calculates live physical measurements for the Real-time Statistics panel."""
        total_kinetic_energy = 0.0
        total_potential_energy = 0.0
        max_velocity = 0.0
        active_bodies_count = 0
        
        # Ground level is approximately at height - 20
        ground_y = self.height - 20.0
        g = abs(self.space.gravity[1])
        
        for body in self.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                active_bodies_count += 1
                m = body.mass
                v = body.velocity.length
                w = body.angular_velocity
                I = body.moment
                
                # E_k = 1/2 m v^2 + 1/2 I w^2
                ek = 0.5 * m * (v ** 2) + 0.5 * I * (w ** 2)
                total_kinetic_energy += ek
                
                if v > max_velocity:
                    max_velocity = v
                    
                # E_p = m g h (height above ground in meters or scale factor)
                # Let 100 pixels = 1 meter
                h_meters = max(0.0, (ground_y - body.position.y) / 100.0)
                ep = m * (g / 100.0) * h_meters
                total_potential_energy += ep

        total_mechanical_energy = total_kinetic_energy + total_potential_energy
        
        return {
            "active_objects": active_bodies_count,
            "kinetic_energy_j": round(total_kinetic_energy / 1000.0, 2), # Scaled J
            "potential_energy_j": round(total_potential_energy / 1000.0, 2),
            "total_energy_j": round(total_mechanical_energy / 1000.0, 2),
            "max_velocity_mps": round(max_velocity / 100.0, 2), # Scaled m/s
            "sim_time_sec": round(self.total_sim_time, 2),
            "gravity": (self.space.gravity[0], self.space.gravity[1]),
            "is_paused": self.paused
        }
