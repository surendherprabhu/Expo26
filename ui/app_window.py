"""
Main Application Window for Universal AI Simulation Environment.
Integrates CustomTkinter dark-mode GUI (40:60 split), Pymunk physics, offscreen Pygame rendering,
real-time telemetry measurements, and conversational OpenAI tool calling.
"""

import time
import tkinter as tk
import customtkinter as ctk
from core.physics_engine import PhysicsEngine
from core.renderer import PhysicsRenderer
from core.ai_agent import AIAgent
from ui.chat_panel import ChatPanel
from ui.stats_panel import StatsPanel
from ui.settings_dialog import SettingsDialog, load_config

APPLICATION_NAME = "UNIVERSAL AI SIMULATION LAB"
SUBTITLE = "SDG 9: Industry, Innovation & Infrastructure"

class AppWindow:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.root = ctk.CTk()
        self.root.title(f"{APPLICATION_NAME} — {SUBTITLE}")
        self.root.configure(bg="#050d1e")
        
        # Center window on screen (1280x820)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = min(1280, int(screen_w * 0.95))
        win_h = min(820, int(screen_h * 0.9))
        pos_x = max(0, int((screen_w - win_w) / 2))
        pos_y = max(0, int((screen_h - win_h) / 2))
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.minsize(1050, 700)

        # Load persisted settings
        self.config = load_config()
        
        # Initialize Core Engines
        # Approximate right panel canvas dimensions: ~760x480
        self.physics = PhysicsEngine(width=760, height=480)
        self.renderer = PhysicsRenderer(self.physics, width=760, height=480)
        self.ai_agent = AIAgent(
            self.physics,
            api_key=self.config.get("api_key", ""),
            model=self.config.get("model", "gpt-4o-mini"),
            base_url=self.config.get("base_url", "")
        )

        # Build UI layout
        self._build_header()
        self._build_main_split()
        self._build_footer()
        
        # Settings Dialog handler
        self.settings_dialog = SettingsDialog(self.root, self._on_settings_saved)

        # Simulation loop state
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Start 60 FPS update cycle
        self._last_time = time.time()
        self._tick_simulation()

    def _build_header(self):
        """Top banner with app branding and connection status."""
        self.header_frame = ctk.CTkFrame(self.root, height=48, fg_color="#0e1117", corner_radius=0)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        # Left branding
        title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=16)
        
        title_lbl = ctk.CTkLabel(
            title_box,
            text=f"⚛ {APPLICATION_NAME}",
            font=("SF Pro", 14, "bold"),
            text_color="#ffffff"
        )
        title_lbl.pack(side="left", padx=(0, 10))

        sdg_badge = ctk.CTkLabel(
            title_box,
            text="SDG 9 / 7 / 12",
            font=("SF Pro", 10, "bold"),
            fg_color="#1f2937",
            text_color="#2fa572",
            corner_radius=4,
            padx=6,
            pady=2
        )
        sdg_badge.pack(side="left")

        # Right connection status
        self.conn_label = ctk.CTkLabel(
            self.header_frame,
            text="Online 🌐" if self.ai_agent.is_online else "Offline 🔌",
            font=("SF Pro", 12, "bold"),
            text_color="#2fa572" if self.ai_agent.is_online else "#8b949e"
        )
        self.conn_label.pack(side="right", padx=16)

    def _build_main_split(self):
        """Builds 40:60 split layout matching user's sketch."""
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=12, pady=10)

        # 40% Left Pane: Chat & Controls
        self.left_pane = ChatPanel(
            self.main_container,
            on_send_message=self._handle_user_message,
            on_reset_world=self._handle_reset_world
        )
        self.left_pane.place(relx=0.0, rely=0.0, relwidth=0.38, relheight=1.0)
        self.left_pane.set_online_status(self.ai_agent.is_online)

        # 60% Right Pane: Physics Simulation Canvas + Statistics Panel
        self.right_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_container.place(relx=0.39, rely=0.0, relwidth=0.61, relheight=1.0)

        # Physics Viewport Frame (Upper ~75%)
        self.viewport_frame = ctk.CTkFrame(
            self.right_container,
            corner_radius=12,
            fg_color="#131722",
            border_width=1,
            border_color="#262c3d"
        )
        self.viewport_frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=0.74)

        # Canvas Header
        cv_header = ctk.CTkFrame(self.viewport_frame, fg_color="transparent", height=32)
        cv_header.pack(fill="x", padx=12, pady=(8, 0))
        cv_header.pack_propagate(False)

        ctk.CTkLabel(
            cv_header,
            text="PHYSICS SIMULATION VIEWPORT (Pymunk 2D Rigid Body)",
            font=("SF Pro", 11, "bold"),
            text_color="#8b949e"
        ).pack(side="left")

        # Pause / Play button
        self.pause_btn = ctk.CTkButton(
            cv_header,
            text="❚❚ Pause",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#2fa572",
            width=65,
            height=22,
            command=self._toggle_pause
        )
        self.pause_btn.pack(side="right", padx=4)

        # Zero-G toggle button
        self.gravity_btn = ctk.CTkButton(
            cv_header,
            text="Gravity: Earth",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#2fa572",
            width=90,
            height=22,
            command=self._cycle_gravity
        )
        self.gravity_btn.pack(side="right", padx=4)

        # Tkinter Canvas for offscreen Pygame blitting
        self.canvas = tk.Canvas(
            self.viewport_frame,
            bg="#0d1117",
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(6, 10))
        
        # Mouse Interaction Events (Pick & Fling objects!)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Real-time Statistics Panel (Lower ~25%)
        self.stats_panel = StatsPanel(self.right_container)
        self.stats_panel.place(relx=0.0, rely=0.76, relwidth=1.0, relheight=0.24)

    def _build_footer(self):
        """Bottom status bar matching user's R.A.P.H.A.E.L layout."""
        self.footer_frame = ctk.CTkFrame(self.root, height=36, fg_color="#0e1117", corner_radius=0)
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)

        # Settings button at bottom left
        self.settings_btn = ctk.CTkButton(
            self.footer_frame,
            text="⚙ Settings",
            font=("SF Pro", 11),
            fg_color="#2fa572",
            hover_color="#106a43",
            width=85,
            height=24,
            corner_radius=6,
            command=self._open_settings
        )
        self.settings_btn.pack(side="left", padx=16)

        # Hint text in middle
        ctk.CTkLabel(
            self.footer_frame,
            text="Click & drag any object in the simulation to interact live",
            font=("SF Pro", 10),
            text_color="#6e7681"
        ).pack(side="left", padx=20)

        # Model label at bottom right
        self.model_label = ctk.CTkLabel(
            self.footer_frame,
            text=f"Model: {self.ai_agent.model}",
            font=("SF Pro", 11),
            text_color="#8b949e"
        )
        self.model_label.pack(side="right", padx=16)

    def _on_canvas_resize(self, event):
        """Update offscreen rendering surface when canvas resizes."""
        if event.width > 100 and event.height > 100:
            self.renderer.resize(event.width, event.height)

    def _on_canvas_click(self, event):
        self.renderer.on_mouse_down(event.x, event.y)

    def _on_canvas_drag(self, event):
        self.renderer.on_mouse_move(event.x, event.y)

    def _on_canvas_release(self, event):
        self.renderer.on_mouse_up()

    def _toggle_pause(self):
        self.physics.paused = not self.physics.paused
        self.pause_btn.configure(text="▶ Play" if self.physics.paused else "❚❚ Pause")

    def _cycle_gravity(self):
        current_gy = self.physics.space.gravity[1]
        if current_gy == 900:
            self.physics.set_gravity(0, 160)
            self.gravity_btn.configure(text="Gravity: Moon")
        elif current_gy == 160:
            self.physics.set_gravity(0, 0)
            self.gravity_btn.configure(text="Gravity: Zero-G")
        else:
            self.physics.set_gravity(0, 900)
            self.gravity_btn.configure(text="Gravity: Earth")

    def _handle_reset_world(self):
        self.physics.reset()
        self.left_pane.append_message("System", "World cleared.")

    def _handle_user_message(self, text: str):
        explanation, actions = self.ai_agent.process_message(text)
        self.root.after(0, lambda: self.left_pane.append_message("AI Agent", explanation, actions))

    def _open_settings(self):
        self.settings_dialog.show()

    def _on_settings_saved(self, new_key: str, new_model: str, new_url: str = ""):
        self.ai_agent.set_api_key(new_key, new_url)
        self.ai_agent.set_model(new_model)
        self.model_label.configure(text=f"Model: {new_model}")
        
        is_on = self.ai_agent.is_online
        self.conn_label.configure(
            text="Online 🌐" if is_on else "Offline 🔌",
            text_color="#2fa572" if is_on else "#8b949e"
        )
        self.left_pane.set_online_status(is_on)

    def _tick_simulation(self):
        """Simulation tick running at ~60 FPS."""
        if not self.running:
            return

        now = time.time()
        dt = min(0.05, now - self._last_time)
        self._last_time = now

        # Step physics engine
        self.physics.step(dt)

        # Render frame to canvas
        photo = self.renderer.render_frame()
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=photo)
        self._cached_photo = photo  # Keep reference to prevent GC

        # Update telemetry stats with dynamic experiment metrics
        telemetry = self.physics.get_dynamic_telemetry()
        self.stats_panel.update_telemetry(telemetry)

        # Schedule next tick (~16ms for 60 FPS)
        self.root.after(16, self._tick_simulation)

    def _on_close(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()
