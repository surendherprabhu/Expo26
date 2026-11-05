"""
Settings Dialog for PROJECT RIA — Research Intelligence Aariz.
Includes two subdivisions:
1. API & Model Configuration (OpenAI, Ollama, custom base URLs).
2. Preset Lab Experiments: Verified scientific experiments with defined aims, apparatus, and conclusions.
"""

import json
import os
import customtkinter as ctk
from core.presets import PRESET_EXPERIMENTS

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
        "base_url": "",
        "gemini_key": os.environ.get("GEMINI_API_KEY", "")
    }

def save_config(config: dict):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

class SettingsDialog:
    def __init__(self, parent, on_save_callback, on_load_preset_callback):
        self.parent = parent
        self.on_save_callback = on_save_callback
        self.on_load_preset_callback = on_load_preset_callback
        self.config = load_config()

    def show(self):
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Settings & Experiment Lab — Universal Simulation")
        self.window.geometry("560x520")
        self.window.resizable(False, False)
        self.window.grab_set()
        self.window.configure(fg_color="#0e1117")

        # Tab view for subdivisions
        self.tabview = ctk.CTkTabview(
            self.window,
            segmented_button_selected_color="#2fa572",
            segmented_button_selected_hover_color="#106a43",
            segmented_button_unselected_color="#1c212d"
        )
        self.tabview.pack(fill="both", expand=True, padx=16, pady=12)

        # Tab 1: AI Model & API Configuration
        self.tab_api = self.tabview.add("AI Model & API")
        self._build_api_tab()

        # Tab 2: Preset Experiments Lab
        self.tab_presets = self.tabview.add("🔬 Preset Experiments")
        self._build_presets_tab()

    def _build_api_tab(self):
        ctk.CTkLabel(
            self.tab_api,
            text="AI Model & API Configuration",
            font=("SF Pro", 15, "bold"),
            text_color="#ffffff"
        ).pack(pady=(10, 12))

        # API Key
        api_frame = ctk.CTkFrame(self.tab_api, fg_color="transparent")
        api_frame.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(api_frame, text="OpenAI API Key (or 'ollama'):", font=("SF Pro", 12)).pack(anchor="w")
        self.api_key_entry = ctk.CTkEntry(
            api_frame,
            placeholder_text="sk-proj-... or ollama",
            show="*",
            width=480,
            height=30,
            fg_color="#1c212d",
            border_color="#262c3d"
        )
        self.api_key_entry.pack(fill="x", pady=(2, 0))
        if self.config.get("api_key"):
            self.api_key_entry.insert(0, self.config["api_key"])

        # Google Gemini API Key (for Vision, Research & Imagen 3)
        gemini_frame = ctk.CTkFrame(self.tab_api, fg_color="transparent")
        gemini_frame.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(gemini_frame, text="Google Gemini API Key (Vision & Research Intelligence):", font=("SF Pro", 12)).pack(anchor="w")
        self.gemini_key_entry = ctk.CTkEntry(
            gemini_frame,
            placeholder_text="AIzaSy...",
            show="*",
            width=480,
            height=30,
            fg_color="#1c212d",
            border_color="#262c3d"
        )
        self.gemini_key_entry.pack(fill="x", pady=(2, 0))
        if self.config.get("gemini_key"):
            self.gemini_key_entry.insert(0, self.config["gemini_key"])

        # Model selection
        model_frame = ctk.CTkFrame(self.tab_api, fg_color="transparent")
        model_frame.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(model_frame, text="Active Model:", font=("SF Pro", 12)).pack(anchor="w")
        self.model_combo = ctk.CTkComboBox(
            model_frame,
            values=["gpt-4o-mini", "gpt-4o", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "qwen3.5:9b"],
            width=480,
            height=30,
            fg_color="#1c212d",
            button_color="#2fa572",
            border_color="#262c3d"
        )
        self.model_combo.pack(fill="x", pady=(2, 0))
        self.model_combo.set(self.config.get("model", "gpt-4o-mini"))

        # Base URL
        url_frame = ctk.CTkFrame(self.tab_api, fg_color="transparent")
        url_frame.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(url_frame, text="Base URL (Leave empty for default):", font=("SF Pro", 12)).pack(anchor="w")
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://api.openai.com/v1 (or http://localhost:11434/v1 for Ollama)",
            width=480,
            height=30,
            fg_color="#1c212d",
            border_color="#262c3d"
        )
        self.url_entry.pack(fill="x", pady=(2, 0))
        if self.config.get("base_url"):
            self.url_entry.insert(0, self.config["base_url"])

        # Presets toggles
        preset_frame = ctk.CTkFrame(self.tab_api, fg_color="transparent")
        preset_frame.pack(fill="x", padx=20, pady=6)
        ctk.CTkButton(
            preset_frame,
            text="OpenAI Default",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#2fa572",
            width=100,
            height=24,
            command=self._set_openai_preset
        ).pack(side="left", padx=(0, 6))
        
        ctk.CTkButton(
            preset_frame,
            text="Google Gemini",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#2fa572",
            width=105,
            height=24,
            command=self._set_gemini_preset
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            preset_frame,
            text="Local Ollama (Qwen)",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#2fa572",
            width=120,
            height=24,
            command=self._set_ollama_preset
        ).pack(side="left")

        # Save Button
        ctk.CTkButton(
            self.tab_api,
            text="Save API Configuration",
            font=("SF Pro", 13, "bold"),
            fg_color="#2fa572",
            hover_color="#106a43",
            height=36,
            corner_radius=8,
            command=self._save
        ).pack(pady=(16, 0), padx=20, fill="x")

    def _build_presets_tab(self):
        ctk.CTkLabel(
            self.tab_presets,
            text="Verified Scientific Experiments",
            font=("SF Pro", 15, "bold"),
            text_color="#ffffff"
        ).pack(pady=(6, 8))

        scroll = ctk.CTkScrollableFrame(self.tab_presets, fg_color="#0e1117", corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        for exp in PRESET_EXPERIMENTS:
            card = ctk.CTkFrame(scroll, fg_color="#161b22", corner_radius=8, border_width=1, border_color="#262c3d")
            card.pack(fill="x", pady=6, padx=4)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(8, 2))
            ctk.CTkLabel(top_row, text=exp["title"], font=("SF Pro", 12, "bold"), text_color="#2fa572").pack(side="left")

            load_btn = ctk.CTkButton(
                top_row,
                text="Load Experiment",
                font=("SF Pro", 10, "bold"),
                fg_color="#2fa572",
                hover_color="#106a43",
                width=110,
                height=24,
                corner_radius=5,
                command=lambda e_id=exp["id"]: self._load_preset(e_id)
            )
            load_btn.pack(side="right")

            # Aim
            ctk.CTkLabel(card, text=f"🎯 Aim: {exp['aim']}", font=("SF Pro", 10), text_color="#c9d1d9", wraplength=480).pack(anchor="w", padx=10, pady=2)
            
            # Theory
            ctk.CTkLabel(card, text=f"📐 Theory: {exp['theoretical_benchmark']}", font=("SF Pro", 10, "bold"), text_color="#58a6ff", wraplength=480).pack(anchor="w", padx=10, pady=2)

            # Conclusion
            ctk.CTkLabel(card, text=f"💡 Conclusion: {exp['conclusion']}", font=("SF Pro", 9), text_color="#8b949e", wraplength=480).pack(anchor="w", padx=10, pady=(2, 8))

    def _set_openai_preset(self):
        self.model_combo.set("gpt-4o-mini")
        self.url_entry.delete(0, "end")

    def _set_gemini_preset(self):
        self.model_combo.set("gemini-2.0-flash")
        self.url_entry.delete(0, "end")

    def _set_ollama_preset(self):
        self.api_key_entry.delete(0, "end")
        self.api_key_entry.insert(0, "ollama")
        self.model_combo.set("qwen3.5:9b")
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, "http://localhost:11434/v1")

    def _load_preset(self, preset_id: str):
        self.on_load_preset_callback(preset_id)
        self.window.destroy()

    def _save(self):
        new_key = self.api_key_entry.get().strip()
        new_gemini_key = self.gemini_key_entry.get().strip()
        new_model = self.model_combo.get().strip()
        new_url = self.url_entry.get().strip()
        
        self.config["api_key"] = new_key
        self.config["gemini_key"] = new_gemini_key
        self.config["model"] = new_model
        self.config["base_url"] = new_url
        save_config(self.config)
        self.on_save_callback(new_key, new_model, new_url, new_gemini_key)
        self.window.destroy()
