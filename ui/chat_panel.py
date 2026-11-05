"""
Chat Panel Module for PROJECT RIA — Research Intelligence Aariz (SDG 9).
40% left pane: Clean experiment protocol log, user prompt input, and send action.
"""

import threading
import customtkinter as ctk
from typing import Callable, Optional

class ChatPanel(ctk.CTkFrame):
    def __init__(self, master, on_send_message: Callable[[str], None], on_reset_world: Callable[[], None], **kwargs):
        super().__init__(master, corner_radius=12, fg_color="#131722", **kwargs)
        self.on_send_message = on_send_message
        self.on_reset_world = on_reset_world
        
        self.attached_image_path = ""
        self._build_top_bar()
        self._build_chat_display()
        self._build_attachment_chip()
        self._build_input_bar()

    def _build_attachment_chip(self):
        self.attachment_chip = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=6)
        self.attachment_lbl = ctk.CTkLabel(
            self.attachment_chip,
            text="📎 Attached Image: None",
            font=("SF Pro", 10),
            text_color="#2fa572"
        )
        self.attachment_lbl.pack(side="left", padx=8, pady=2)
        
        del_btn = ctk.CTkButton(
            self.attachment_chip,
            text="✕",
            font=("SF Pro", 9),
            width=18,
            height=18,
            fg_color="transparent",
            hover_color="#ef4444",
            command=self._clear_attachment
        )
        del_btn.pack(side="right", padx=4)

    def _on_attach_image(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Attach Physical Diagram / Sketch",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp"), ("All Files", "*.*")]
        )
        if file_path:
            self.attached_image_path = file_path
            self.attachment_lbl.configure(text=f"📎 Image: {os.path.basename(file_path)}")
            self.attachment_chip.pack(fill="x", padx=12, pady=(0, 4), before=self.input_frame)

    def _clear_attachment(self):
        self.attached_image_path = ""
        self.attachment_chip.pack_forget()

    def _build_top_bar(self):
        """Clean header without redundant online status (handled in top window bar)."""
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=12, pady=(10, 6))
        
        title_lbl = ctk.CTkLabel(
            top_frame,
            text="💬 EXPERIMENT LOG & PROTOCOL",
            font=("SF Pro", 11, "bold"),
            text_color="#8b949e"
        )
        title_lbl.pack(side="left")
        
        self.clear_btn = ctk.CTkButton(
            top_frame,
            text="↺ Clear",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#3d4455",
            width=65,
            height=24,
            corner_radius=5,
            command=self.on_reset_world
        )
        self.clear_btn.pack(side="right")

    def _build_chat_display(self):
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
        
        self.append_message(
            "System",
            "PROJECT RIA initialized (Research Intelligence Aariz).\n"
            "Describe any physical experiment (e.g. Galileo's drop, friction on a wedge, skid braking, or elastic collisions).\n"
            "Apparatus will construct in an enclosed chamber and freeze at t=0.0s ready for release."
        )

    def _build_input_bar(self):
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=12, pady=(6, 12))

        self.btn_attach = ctk.CTkButton(
            self.input_frame,
            text="📷",
            font=("SF Pro", 13),
            width=36,
            height=36,
            fg_color="#1c212d",
            hover_color="#2fa572",
            corner_radius=8,
            command=self._on_attach_image
        )
        self.btn_attach.pack(side="left", padx=(0, 6))

        self.input_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Describe a simulation or attach diagram...",
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
            self.input_frame,
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
        img = self.attached_image_path
        if not text and not img:
            return
            
        if not text and img:
            text = "Analyze this uploaded diagram and reconstruct this physical experiment inside the chamber."
            
        self.input_entry.delete(0, "end")
        self._clear_attachment()
        
        display_msg = text
        if img:
            display_msg += f"\n[Attached Diagram: {os.path.basename(img)}]"
        self.append_message("You", display_msg)
        
        self.send_btn.configure(state="disabled")
        
        def run():
            try:
                self.on_send_message(text, img)
            finally:
                self.after(0, lambda: self.send_btn.configure(state="normal"))

        threading.Thread(target=run, daemon=True).start()

    def set_online_status(self, is_online: bool):
        pass

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
