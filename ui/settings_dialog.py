"""
Settings Dialog for Universal AI Simulation Environment.
Lets user set OpenAI API Key, choose model, and persist settings in config.json.
"""

import json
import os
import customtkinter as ctk

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "model": "gpt-4o-mini"
    }

def save_config(config: dict):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

class SettingsDialog:
    def __init__(self, parent, on_save_callback):
        self.parent = parent
        self.on_save_callback = on_save_callback
        self.config = load_config()

    def show(self):
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Settings — AI Simulation Engine")
        self.window.geometry("450x320")
        self.window.resizable(False, False)
        self.window.grab_set()  # Modal
        self.window.configure(fg_color="#0e1117")

        # Title
        ctk.CTkLabel(
            self.window,
            text="AI Model & API Configuration",
            font=("SF Pro", 16, "bold"),
            text_color="#ffffff"
        ).pack(pady=(20, 15))

        # API Key field
        api_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        api_frame.pack(fill="x", padx=30, pady=5)
        
        ctk.CTkLabel(api_frame, text="OpenAI API Key:", font=("SF Pro", 12)).pack(anchor="w")
        self.api_key_entry = ctk.CTkEntry(
            api_frame,
            placeholder_text="sk-proj-...",
            show="*",
            width=380,
            height=32,
            fg_color="#1c212d",
            border_color="#262c3d"
        )
        self.api_key_entry.pack(fill="x", pady=(4, 0))
        if self.config.get("api_key"):
            self.api_key_entry.insert(0, self.config["api_key"])

        # Model selection
        model_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        model_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(model_frame, text="Select Model:", font=("SF Pro", 12)).pack(anchor="w")
        self.model_combo = ctk.CTkComboBox(
            model_frame,
            values=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
            width=380,
            height=32,
            fg_color="#1c212d",
            button_color="#2fa572",
            button_hover_color="#106a43",
            border_color="#262c3d"
        )
        self.model_combo.pack(fill="x", pady=(4, 0))
        current_model = self.config.get("model", "gpt-4o-mini")
        self.model_combo.set(current_model)

        # Save button
        ctk.CTkButton(
            self.window,
            text="Save Settings",
            font=("SF Pro", 13, "bold"),
            fg_color="#2fa572",
            hover_color="#106a43",
            height=36,
            corner_radius=8,
            command=self._save
        ).pack(pady=(20, 0), padx=30, fill="x")

    def _save(self):
        new_key = self.api_key_entry.get().strip()
        new_model = self.model_combo.get().strip()
        self.config["api_key"] = new_key
        self.config["model"] = new_model
        save_config(self.config)
        self.on_save_callback(new_key, new_model)
        self.window.destroy()
