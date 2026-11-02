"""
Main Application Window for Universal AI Simulation Environment (SDG 9).
Integrates:
- 40:60 Split CustomTkinter interface
- Pymunk 2D physics engine with solid triangular wedges
- Experiment Freeze at t=0.0s with explicit [▶ Release / Run] control
- Toggleable Mouse Grab interaction switch
- Dynamic telemetry & Formal Experiment Control Sheet / Report
- Settings menu with Preset Experiments library
"""

import time
import tkinter as tk
import customtkinter as ctk
from core.physics_engine import PhysicsEngine
from core.renderer import PhysicsRenderer
from core.ai_agent import AIAgent
from core.presets import load_preset_by_id
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
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = min(1280, int(screen_w * 0.95))
        win_h = min(820, int(screen_h * 0.9))
        pos_x = max(0, int((screen_w - win_w) / 2))
        pos_y = max(0, int((screen_h - win_h) / 2))
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.minsize(1050, 700)

        self.config = load_config()
        
        # Initialize Core Engines
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
        
        self.settings_dialog = SettingsDialog(
            self.root,
            on_save_callback=self._on_settings_saved,
            on_load_preset_callback=self._on_load_preset
        )

        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._last_time = time.time()
        self._tick_simulation()

    def _build_header(self):
        self.header_frame = ctk.CTkFrame(self.root, height=48, fg_color="#0e1117", corner_radius=0)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

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

        self.conn_label = ctk.CTkLabel(
            self.header_frame,
            text="Online 🌐" if self.ai_agent.is_online else "Offline 🔌",
            font=("SF Pro", 12, "bold"),
            text_color="#2fa572" if self.ai_agent.is_online else "#8b949e"
        )
        self.conn_label.pack(side="right", padx=16)

    def _build_main_split(self):
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=12, pady=10)

        # 40% Left Pane: Chat
        self.left_pane = ChatPanel(
            self.main_container,
            on_send_message=self._handle_user_message,
            on_reset_world=self._handle_reset_world
        )
        self.left_pane.place(relx=0.0, rely=0.0, relwidth=0.38, relheight=1.0)
        self.left_pane.set_online_status(self.ai_agent.is_online)

        # 60% Right Pane: Viewport + Telemetry/Report
        self.right_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_container.place(relx=0.39, rely=0.0, relwidth=0.61, relheight=1.0)

        # Viewport Frame (Upper ~75%)
        self.viewport_frame = ctk.CTkFrame(
            self.right_container,
            corner_radius=12,
            fg_color="#131722",
            border_width=1,
            border_color="#262c3d"
        )
        self.viewport_frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=0.74)

        # Canvas Header Controls
        cv_header = ctk.CTkFrame(self.viewport_frame, fg_color="transparent", height=34)
        cv_header.pack(fill="x", padx=10, pady=(6, 0))
        cv_header.pack_propagate(False)

        ctk.CTkLabel(
            cv_header,
            text="APPARATUS VIEWPORT",
            font=("SF Pro", 11, "bold"),
            text_color="#8b949e"
        ).pack(side="left")

        # Mouse Grab Toggle Switch
        self.mouse_switch = ctk.CTkSwitch(
            cv_header,
            text="Mouse Grab",
            font=("SF Pro", 10),
            progress_color="#2fa572",
            command=self._on_toggle_mouse
        )
        self.mouse_switch.pack(side="left", padx=(14, 0))
        self.mouse_switch.select()

        # Primary Release / Run button
        self.run_btn = ctk.CTkButton(
            cv_header,
            text="▶ Release / Run",
            font=("SF Pro", 10, "bold"),
            fg_color="#2fa572",
            hover_color="#106a43",
            width=100,
            height=24,
            command=self._toggle_run
        )
        self.run_btn.pack(side="right", padx=3)

        # Reset to t=0 button
        self.reset_t0_btn = ctk.CTkButton(
            cv_header,
            text="↺ Reset (t=0)",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#3d4455",
            width=85,
            height=24,
            command=self._reset_to_t0
        )
        self.reset_t0_btn.pack(side="right", padx=3)

        # End Experiment & Report button
        self.end_exp_btn = ctk.CTkButton(
            cv_header,
            text="📋 End & Report",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#58a6ff",
            width=90,
            height=24,
            command=self._on_end_experiment
        )
        self.end_exp_btn.pack(side="right", padx=3)

        # Tkinter Canvas for offscreen Pygame rendering
        self.canvas = tk.Canvas(
            self.viewport_frame,
            bg="#0d1117",
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Statistics / Control Sheet Panel (Lower ~25%)
        self.stats_panel = StatsPanel(self.right_container, on_end_experiment=self._on_end_experiment)
        self.stats_panel.place(relx=0.0, rely=0.76, relwidth=1.0, relheight=0.24)

    def _build_footer(self):
        self.footer_frame = ctk.CTkFrame(self.root, height=36, fg_color="#0e1117", corner_radius=0)
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)

        self.settings_btn = ctk.CTkButton(
            self.footer_frame,
            text="⚙ Settings & Presets",
            font=("SF Pro", 11),
            fg_color="#2fa572",
            hover_color="#106a43",
            width=140,
            height=24,
            corner_radius=6,
            command=self._open_settings
        )
        self.settings_btn.pack(side="left", padx=16)

        ctk.CTkLabel(
            self.footer_frame,
            text="Click '▶ Release / Run' to trigger motion. Toggle Mouse Grab to interact.",
            font=("SF Pro", 10),
            text_color="#6e7681"
        ).pack(side="left", padx=10)

        self.model_label = ctk.CTkLabel(
            self.footer_frame,
            text=f"Model: {self.ai_agent.model}",
            font=("SF Pro", 11),
            text_color="#8b949e"
        )
        self.model_label.pack(side="right", padx=16)

    def _on_toggle_mouse(self):
        is_on = bool(self.mouse_switch.get())
        self.renderer.set_mouse_interaction(is_on)
        self.canvas.configure(cursor="hand2" if is_on else "arrow")

    def _on_canvas_resize(self, event):
        if event.width > 100 and event.height > 100:
            self.renderer.resize(event.width, event.height)

    def _on_canvas_click(self, event):
        self.renderer.on_mouse_down(event.x, event.y)

    def _on_canvas_drag(self, event):
        self.renderer.on_mouse_move(event.x, event.y)

    def _on_canvas_release(self, event):
        self.renderer.on_mouse_up()

    def _toggle_run(self):
        self.physics.paused = not self.physics.paused
        if self.physics.paused:
            self.run_btn.configure(text="▶ Resume", fg_color="#2fa572")
        else:
            self.run_btn.configure(text="❚❚ Pause", fg_color="#e67e22")
            self.stats_panel.show_telemetry_view()

    def _reset_to_t0(self):
        self.physics.reset_to_initial_state()
        self.run_btn.configure(text="▶ Release / Run", fg_color="#2fa572")
        self.stats_panel.show_telemetry_view()
        self.left_pane.append_message("System", "Apparatus reset to initial state (t = 0.00s). Ready for release.")

    def _on_end_experiment(self):
        self.physics.paused = True
        self.run_btn.configure(text="▶ Release / Run", fg_color="#2fa572")
        report = self.physics.generate_experiment_report()
        self.stats_panel.set_report_data(report)
        self.left_pane.append_message("System", f"Experiment ended. Control sheet generated for '{report.get('title')}'.")

    def _handle_reset_world(self):
        self.physics.reset()
        self.run_btn.configure(text="▶ Release / Run", fg_color="#2fa572")
        self.left_pane.append_message("System", "World cleared.")

    def _handle_user_message(self, text: str):
        explanation, actions = self.ai_agent.process_message(text)
        self.root.after(0, lambda: self._on_message_finished(explanation, actions))

    def _on_message_finished(self, explanation: str, actions: list):
        self.left_pane.append_message("AI Agent", explanation, actions)
        # Apparatus is frozen at t=0 ready for user
        self.run_btn.configure(text="▶ Release / Run", fg_color="#2fa572")
        self.stats_panel.show_telemetry_view()

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

    def _on_load_preset(self, preset_id: str):
        preset = load_preset_by_id(self.physics, preset_id)
        self.run_btn.configure(text="▶ Release / Run", fg_color="#2fa572")
        self.stats_panel.show_telemetry_view()
        
        # Post crisp experiment protocol into chat
        self.left_pane.append_message(
            "System",
            f"🧪 Loaded Preset: {preset['title']}\n"
            f"• Aim: {preset['aim']}\n"
            f"• Theoretical Benchmark: {preset['theoretical_benchmark']}\n"
            f"• Status: Apparatus frozen at t=0.00s. Click 'Release / Run' to begin."
        )

    def _tick_simulation(self):
        if not self.running:
            return

        now = time.time()
        dt = min(0.05, now - self._last_time)
        self._last_time = now

        self.physics.step(dt)

        photo = self.renderer.render_frame()
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=photo)
        self._cached_photo = photo

        telemetry = self.physics.get_dynamic_telemetry()
        self.stats_panel.update_telemetry(telemetry)

        self.root.after(16, self._tick_simulation)

    def _on_close(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()
