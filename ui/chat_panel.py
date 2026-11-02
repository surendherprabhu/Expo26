"""
Chat Panel Module for Universal AI Simulation Environment.
40% left pane: Displays conversation history, status, quick demo presets, and user prompt input.
"""

import threading
import customtkinter as ctk
from typing import Callable, Optional

class ChatPanel(ctk.CTkFrame):
    def __init__(self, master, on_send_message: Callable[[str], None], on_reset_world: Callable[[], None], **kwargs):
        super().__init__(master, corner_radius=12, fg_color="#131722", **kwargs)
        self.on_send_message = on_send_message
        self.on_reset_world = on_reset_world
        
        self._build_top_bar()
        self._build_presets_bar()
        self._build_chat_display()
        self._build_input_bar()

    def _build_top_bar(self):
        """Top bar matching user's sketch: Status indicator & quick reset button."""
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=12, pady=(10, 4))
        
        # Left status indicator
        self.status_label = ctk.CTkLabel(
            top_frame,
            text="Online 🌐",
            font=("SF Pro", 12, "bold"),
            text_color="#2fa572"
        )
        self.status_label.pack(side="left")
        
        # Right action button ("IDK / Random Button" from sketch -> Quick Clear/Reset)
        self.reset_btn = ctk.CTkButton(
            top_frame,
            text="↺ Clear World",
            font=("SF Pro", 11),
            fg_color="#2b313e",
            hover_color="#3d4455",
            width=90,
            height=26,
            corner_radius=6,
            command=self.on_reset_world
        )
        self.reset_btn.pack(side="right")

    def _build_presets_bar(self):
        """Quick demo buttons for instant testing and presentation."""
        preset_frame = ctk.CTkFrame(self, fg_color="transparent")
        preset_frame.pack(fill="x", padx=12, pady=(0, 6))

        presets = [
            ("Newton's Cradle", "Simulate a 5-ball Newton's Cradle"),
            ("Truss Bridge", "Build a pinned bridge span with a heavy test load"),
            ("Ramp & Sphere", "Create an inclined ramp with rolling and sliding bodies"),
            ("Block Tower", "Stack a 5-block vertical tower")
        ]

        for label, prompt in presets:
            btn = ctk.CTkButton(
                preset_frame,
                text=label,
                font=("SF Pro", 10),
                fg_color="#1c212d",
                hover_color="#2fa572",
                text_color="#c9d1d9",
                height=22,
                corner_radius=5,
                command=lambda p=prompt: self._trigger_preset(p)
            )
            btn.pack(side="left", padx=2, expand=True, fill="x")

    def _trigger_preset(self, prompt: str):
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, prompt)
        self._handle_send()

    def _build_chat_display(self):
        """Scrollable chat history with word wrapping."""
        self.chat_box = ctk.CTkTextbox(
            self,
            wrap="word",
            state="normal",
            font=("SF Pro", 12),
            fg_color="#0e1117",
            text_color="#e6edf3",
            corner_radius=8,
            border_width=1,
            border_color="#262c3d"
        )
        self.chat_box.pack(fill="both", expand=True, padx=12, pady=4)
        
        # Welcome message
        self.append_message(
            "System",
            "Universal AI Simulation Lab initialized.\n"
            "Ask me to construct physical mechanisms, structural trusses, collision tests, or energy networks conversationally.\n"
            "You can also click and fling any object in the physics canvas with your mouse!"
        )

    def _build_input_bar(self):
        """Bottom user input and green send button matching user's R.A.P.H.A.E.L styling."""
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=12, pady=(6, 12))

        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Describe a system (e.g. 'Build a bridge and drop a 40kg load')...",
            font=("SF Pro", 12),
            fg_color="#1c212d",
            border_color="#262c3d",
            text_color="#ffffff",
            corner_radius=8,
            height=36
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.input_entry.bind("<Return>", lambda e: self._handle_send())

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            font=("SF Pro", 12, "bold"),
            fg_color="#2fa572",
            hover_color="#106a43",
            corner_radius=8,
            width=70,
            height=36,
            command=self._handle_send
        )
        self.send_btn.pack(side="right")

    def _handle_send(self):
        text = self.input_entry.get().strip()
        if not text:
            return
        self.input_entry.delete(0, "end")
        self.append_message("You", text)
        
        # Disable send while processing
        self.send_btn.configure(state="disabled")
        
        def run():
            try:
                self.on_send_message(text)
            finally:
                self.after(0, lambda: self.send_btn.configure(state="normal"))

        threading.Thread(target=run, daemon=True).start()

    def set_online_status(self, is_online: bool):
        if is_online:
            self.status_label.configure(text="Online 🌐", text_color="#2fa572")
        else:
            self.status_label.configure(text="Offline 🔌", text_color="#8b949e")

    def append_message(self, sender: str, text: str, actions: Optional[list] = None):
        self.chat_box.configure(state="normal")
        
        if sender == "You":
            self.chat_box.insert("end", f"\n👤 User:\n{text}\n", "user_tag")
        elif sender == "System":
            self.chat_box.insert("end", f"\n⚙️ {sender}:\n{text}\n", "sys_tag")
        else:
            self.chat_box.insert("end", f"\n🤖 AI Agent:\n{text}\n", "ai_tag")
            if actions:
                for act in actions:
                    self.chat_box.insert("end", f"   ↳ 🔧 {act}\n", "action_tag")

        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")
