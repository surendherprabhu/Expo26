"""
Settings Dialog for Universal AI Simulation Environment.
Lets user set API Key, select model, and optionally configure custom endpoint (OpenAI vs local Ollama).
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
        "model": "gpt-4o-mini",
        "base_url": ""
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
        self.window.geometry("480x400")
        self.window.resizable(False, False)
        self.window.grab_set()  # Modal
        self.window.configure(fg_color="#0e1117")

        # Title
        ctk.CTkLabel(
            self.window,
            text="AI Model & API Configuration",
            font=("SF Pro", 16, "bold"),
            text_color="#ffffff"
        ).pack(pady=(16, 12))

        # API Key field
        api_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        api_frame.pack(fill="x", padx=30, pady=4)
        
        ctk.CTkLabel(api_frame, text="API Key (OpenAI or 'ollama'):", font=("SF Pro", 12)).pack(anchor="w")
        self.api_key_entry = ctk.CTkEntry(
            api_frame,
            placeholder_text="sk-proj-... or ollama",
            show="*",
            width=420,
            height=32,
            fg_color="#1c212d",
            border_color="#262c3d"
        )
        self.api_key_entry.pack(fill="x", pady=(4, 0))
        if self.config.get("api_key"):
            self.api_key_entry.insert(0, self.config["api_key"])

        # Model selection
        model_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        model_frame.pack(fill="x", padx=30, pady=8)
        
        ctk.CTkLabel(model_frame, text="Select Model:", font=("SF Pro", 12)).pack(anchor="w")
        self.model_combo = ctk.CTkComboBox(
            model_frame,
            values=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "qwen3.5:9b"],
            width=420,
            height=32,
            fg_color="#1c212d",
            button_color="#2fa572",
            button_hover_color="#106a43",
            border_color="#262c3d"
        )
        self.model_combo.pack(fill="x", pady=(4, 0))
        current_model = self.config.get("model", "gpt-4o-mini")
        self.model_combo.set(current_model)

        # Base URL (for OpenAI or Local Ollama)
        url_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        url_frame.pack(fill="x", padx=30, pady=8)
        
        ctk.CTkLabel(url_frame, text="API Base URL (Leave empty for standard OpenAI):", font=("SF Pro", 12)).pack(anchor="w")
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://api.openai.com/v1 (or http://localhost:11434/v1 for Ollama)",
            width=420,
            height=32,
            fg_color="#1c212d",
            border_color="#262c3d"
        )
        self.url_entry.pack(fill="x", pady=(4, 0))
        if self.config.get("base_url"):
            self.url_entry.insert(0, self.config["base_url"])

        # Quick preset buttons for convenience
        preset_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        preset_frame.pack(fill="x", padx=30, pady=2)
        ctk.CTkButton(
            preset_frame,
            text="Use OpenAI Default",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#2fa572",
            width=140,
            height=22,
            command=self._set_openai_preset
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkButton(
            preset_frame,
            text="Use Local Ollama",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#2fa572",
            width=140,
            height=22,
            command=self._set_ollama_preset
        ).pack(side="left")

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
        ).pack(pady=(16, 0), padx=30, fill="x")

    def _set_openai_preset(self):
        self.model_combo.set("gpt-4o-mini")
        self.url_entry.delete(0, "end")

    def _set_ollama_preset(self):
        self.api_key_entry.delete(0, "end")
        self.api_key_entry.insert(0, "ollama")
        self.model_combo.set("qwen3.5:9b")
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, "http://localhost:11434/v1")

    def _save(self):
        new_key = self.api_key_entry.get().strip()
        new_model = self.model_combo.get().strip()
        new_url = self.url_entry.get().strip()
        self.config["api_key"] = new_key
        self.config["model"] = new_model
        self.config["base_url"] = new_url
        save_config(self.config)
        self.on_save_callback(new_key, new_model, new_url)
        self.window.destroy()
