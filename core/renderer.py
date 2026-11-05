"""
Renderer Module for PROJECT RIA — Research Intelligence Aariz.
Renders Pymunk rigid bodies inside an enclosed 4-wall laboratory viewport.
Features:
- Center-of-mass mouse grabbing (zero unwanted off-center rotational torque)
- Visual closed-room boundary frame
- Light lab / Dark mode theme toggle
- Ghost line prevention on reset
"""

import os
import math
import pygame
import pymunk
import pymunk.pygame_util
from PIL import Image, ImageTk
from typing import Optional, Tuple

class PhysicsRenderer:
    def __init__(self, physics_engine, width: int = 760, height: int = 480):
        self.engine = physics_engine
        self.width = width
        self.height = height
        self.mouse_enabled = True
        self.theme = "light"  # Default light laboratory theme
        
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        
        self.surface = pygame.Surface((self.width, self.height))
        self.draw_options = pymunk.pygame_util.DrawOptions(self.surface)
        
        self._apply_theme_colors()
        self._init_mouse_body()
        self._last_photo = None

    def _init_mouse_body(self):
        self.mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.mouse_joint: Optional[pymunk.PivotJoint] = None
        self.grabbed_body: Optional[pymunk.Body] = None
        self.grabbed_initial_angle: float = 0.0
        self.grab_polar_angle: float = 0.0
        self.engine.space.add(self.mouse_body)

    def _apply_theme_colors(self):
        if self.theme == "light":
            self.bg_color = (248, 250, 252)        # Crisp lab canvas (#f8fafc)
            self.grid_color = (226, 232, 240)      # Subtle grid (#e2e8f0)
            self.wall_color = (71, 85, 105)        # Clean slate boundary frame (#475569)
            self.floor_line = (30, 41, 59)         # Dark bench line
            self.accent_color = (16, 185, 129)     # Emerald (#10b981)
        else:
            self.bg_color = (13, 17, 23)
            self.grid_color = (30, 41, 59)
            self.wall_color = (71, 85, 105)
            self.floor_line = (148, 163, 184)
            self.accent_color = (47, 165, 114)

    def set_theme(self, theme_name: str):
        self.theme = theme_name.lower()
        self._apply_theme_colors()

    def set_mouse_interaction(self, enabled: bool):
        self.mouse_enabled = enabled
        if not enabled:
            self.release_mouse()

    def release_mouse(self):
        """Immediately disconnects and cleans up any mouse joint and references."""
        if self.mouse_joint is not None:
            try:
                if self.mouse_joint in self.engine.space.constraints:
                    self.engine.space.remove(self.mouse_joint)
            except Exception:
                pass
            self.mouse_joint = None
        self.grabbed_body = None

    def resize(self, width: int, height: int):
        if width > 50 and height > 50 and (width != self.width or height != self.height):
            self.width = width
            self.height = height
            self.engine.set_dimensions(width, height)
            self.surface = pygame.Surface((self.width, self.height))
            self.draw_options = pymunk.pygame_util.DrawOptions(self.surface)

    def on_mouse_down(self, x: float, y: float):
        """
        Grabs object at its CENTER OF MASS (anchor_b=(0,0)) to eliminate
        unwanted rotational torque so the body doesn't spin wildly.
        Tracks cursor angle so circular cursor motion rotates the body intentionally.
        """
        if not self.mouse_enabled:
            return
            
        self.release_mouse()
        self.mouse_body.position = (x, y)
        point_info = self.engine.space.point_query_nearest((x, y), 35.0, pymunk.ShapeFilter())
        
        if point_info and point_info.shape and point_info.shape.body.body_type == pymunk.Body.DYNAMIC:
            body = point_info.shape.body
            self.grabbed_body = body
            self.grabbed_initial_angle = body.angle
            body.angular_velocity = 0.0
            
            # Record initial polar angle from body center to cursor
            dx = x - body.position.x
            dy = y - body.position.y
            self.grab_polar_angle = math.atan2(dy, dx)
            
            # Pivot joint connected directly to body center of mass (0, 0)
            self.mouse_joint = pymunk.PivotJoint(self.mouse_body, body, (0, 0), (0, 0))
            self.mouse_joint.max_force = 60000.0
            self.mouse_joint.error_bias = (1.0 - 0.20) ** 60.0
            self.engine.space.add(self.mouse_joint)

    def on_mouse_move(self, x: float, y: float):
        if not self.mouse_enabled or not self.mouse_joint or not self.grabbed_body:
            return
            
        # Clamp mouse body position inside closed room
        cx = max(20.0, min(self.width - 20.0, x))
        cy = max(20.0, min(self.height - 20.0, y))
        self.mouse_body.position = (cx, cy)
        
        # Suppress rotational spin while translating body
        body = self.grabbed_body
        body.angular_velocity = 0.0
        
        # If cursor circles around the body center, rotate body in response
        dx = x - body.position.x
        dy = y - body.position.y
        dist = math.hypot(dx, dy)
        if dist > 20.0:
            current_polar = math.atan2(dy, dx)
            delta_theta = current_polar - self.grab_polar_angle
            body.angle = self.grabbed_initial_angle + delta_theta

    def on_mouse_up(self):
        self.release_mouse()

    def render_frame(self) -> ImageTk.PhotoImage:
        self.surface.fill(self.bg_color)
        
        # Draw architectural grid
        grid_step = 50
        for gx in range(0, self.width, grid_step):
            pygame.draw.line(self.surface, self.grid_color, (gx, 0), (gx, self.height), 1)
        for gy in range(0, self.height, grid_step):
            pygame.draw.line(self.surface, self.grid_color, (0, gy), (self.width, gy), 1)

        # Draw Pymunk bodies via debug_draw
        self.engine.space.debug_draw(self.draw_options)

        # Draw visible closed chamber perimeter frame (floor, ceiling, walls)
        t = 14
        pygame.draw.rect(self.surface, self.wall_color, (0, 0, self.width, self.height), t)
        # Highlight floor line
        pygame.draw.line(self.surface, self.floor_line, (0, self.height - t), (self.width, self.height - t), 2)

        # Draw mouse interaction handle
        if self.mouse_enabled and self.mouse_joint:
            # Check validity in case world was reset or body was removed
            if self.mouse_joint not in self.engine.space.constraints or not self.mouse_joint.b:
                self.release_mouse()
            else:
                anchor_a = self.mouse_body.position
                anchor_b = self.mouse_joint.b.position
                pygame.draw.line(self.surface, self.accent_color, (int(anchor_a.x), int(anchor_a.y)), (int(anchor_b.x), int(anchor_b.y)), 2)
                pygame.draw.circle(self.surface, (16, 185, 129), (int(anchor_a.x), int(anchor_a.y)), 4)

        raw_data = pygame.image.tobytes(self.surface, "RGBA")
        pil_img = Image.frombytes("RGBA", (self.width, self.height), raw_data)
        self._last_photo = ImageTk.PhotoImage(pil_img)
        return self._last_photo
