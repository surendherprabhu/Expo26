"""
Renderer Module for Universal AI Simulation Environment.
Renders Pymunk rigid bodies onto an offscreen Pygame surface with dark-mode aesthetic,
and converts frames to PIL ImageTk for seamless embedding in CustomTkinter.
Supports toggleable mouse picking and flinging.
"""

import os
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
        self.mouse_enabled = True  # Toggleable via UI switch
        
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        
        self.surface = pygame.Surface((self.width, self.height))
        self.draw_options = pymunk.pygame_util.DrawOptions(self.surface)
        
        # Stylistic colors
        self.bg_color = (13, 17, 23)
        self.grid_color = (25, 32, 44)
        self.accent_green = (47, 165, 114)
        
        # Mouse interaction state
        self.mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.mouse_joint: Optional[pymunk.PivotJoint] = None
        self.engine.space.add(self.mouse_body)
        
        self._last_photo = None

    def set_mouse_interaction(self, enabled: bool):
        """Enables or disables manual mouse grabbing/dragging."""
        self.mouse_enabled = enabled
        if not enabled and self.mouse_joint:
            self.engine.space.remove(self.mouse_joint)
            self.mouse_joint = None

    def resize(self, width: int, height: int):
        """Resizes the offscreen render surface."""
        if width > 50 and height > 50 and (width != self.width or height != self.height):
            self.width = width
            self.height = height
            self.engine.width = width
            self.engine.height = height
            self.surface = pygame.Surface((self.width, self.height))
            self.draw_options = pymunk.pygame_util.DrawOptions(self.surface)

    def on_mouse_down(self, x: float, y: float):
        """User clicks on physics canvas: pick up nearest dynamic body if enabled."""
        if not self.mouse_enabled:
            return
        self.mouse_body.position = (x, y)
        point_info = self.engine.space.point_query_nearest((x, y), 25.0, pymunk.ShapeFilter())
        
        if point_info and point_info.shape and point_info.shape.body.body_type == pymunk.Body.DYNAMIC:
            body = point_info.shape.body
            self.mouse_joint = pymunk.PivotJoint(self.mouse_body, body, (x, y))
            self.mouse_joint.max_force = 50000.0
            self.mouse_joint.error_bias = (1.0 - 0.15) ** 60.0
            self.engine.space.add(self.mouse_joint)

    def on_mouse_move(self, x: float, y: float):
        """Update dragged body position."""
        if not self.mouse_enabled:
            return
        self.mouse_body.position = (x, y)

    def on_mouse_up(self):
        """Release grabbed body."""
        if self.mouse_joint:
            self.engine.space.remove(self.mouse_joint)
            self.mouse_joint = None

    def render_frame(self) -> ImageTk.PhotoImage:
        """Renders one frame and returns an ImageTk.PhotoImage for Tkinter."""
        self.surface.fill(self.bg_color)
        
        # Subtle background grid
        grid_step = 50
        for gx in range(0, self.width, grid_step):
            pygame.draw.line(self.surface, self.grid_color, (gx, 0), (gx, self.height), 1)
        for gy in range(0, self.height, grid_step):
            pygame.draw.line(self.surface, self.grid_color, (0, gy), (self.width, gy), 1)

        # Draw Pymunk bodies
        self.engine.space.debug_draw(self.draw_options)

        # Highlight mouse interaction line if active
        if self.mouse_enabled and self.mouse_joint:
            anchor_a = self.mouse_body.position
            anchor_b = self.mouse_joint.b.position
            pygame.draw.line(self.surface, self.accent_green, (int(anchor_a.x), int(anchor_a.y)), (int(anchor_b.x), int(anchor_b.y)), 2)
            pygame.draw.circle(self.surface, (255, 255, 255), (int(anchor_a.x), int(anchor_a.y)), 4)

        # Convert to PIL Image -> ImageTk PhotoImage
        raw_data = pygame.image.tobytes(self.surface, "RGBA")
        pil_img = Image.frombytes("RGBA", (self.width, self.height), raw_data)
        self._last_photo = ImageTk.PhotoImage(pil_img)
        return self._last_photo
