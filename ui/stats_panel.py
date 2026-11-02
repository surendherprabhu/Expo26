"""
Dynamic Real-Time Statistics & Measurements Panel.
Renders scientific variables dynamically defined by the AI model for the active experiment,
replacing static placeholders with real physics metrics matching what is happening on screen.
"""

import customtkinter as ctk
from typing import Dict, List, Any

class StatsPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=12, fg_color="#131722", **kwargs)
        
        # Header title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=14, pady=(10, 6))
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ EXPERIMENT MEASUREMENTS & TELEMETRY",
            font=("SF Pro", 12, "bold"),
            text_color="#8b949e"
        )
        self.title_label.pack(side="left")
        
        self.status_badge = ctk.CTkLabel(
            header_frame,
            text="● 60 FPS",
            font=("SF Pro", 11, "bold"),
            text_color="#2fa572"
        )
        self.status_badge.pack(side="right")

        # Container for dynamic metric cards
        self.metrics_container = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # Placeholder label when no experiment variables are configured yet
        self.placeholder_lbl = ctk.CTkLabel(
            self.metrics_container,
            text="Awaiting experiment variables from AI...\nAsk the AI to simulate a system (e.g. an inclined plane or pendulum).",
            font=("SF Pro", 11),
            text_color="#555f6d"
        )
        self.placeholder_lbl.pack(expand=True, pady=16)

        # Cache of active card widgets: {metric_id: (card_frame, val_label)}
        self.cards: Dict[str, Any] = {}
        self._current_metric_keys: List[str] = []

    def _rebuild_cards(self, metric_items: List[Dict[str, Any]]):
        """Reconstructs dynamic cards using pack(side='left') when AI configures new variables."""
        if self.placeholder_lbl.winfo_ismapped():
            self.placeholder_lbl.pack_forget()

        for card_frame, _ in self.cards.values():
            card_frame.destroy()
        self.cards.clear()

        for item in metric_items:
            m_id = item["id"]
            name = item["name"]
            unit = item["unit"]

            card = ctk.CTkFrame(
                self.metrics_container,
                fg_color="#1c212d",
                corner_radius=8,
                border_width=1,
                border_color="#262c3d"
            )
            card.pack(side="left", fill="both", expand=True, padx=4, pady=2)

            lbl = ctk.CTkLabel(card, text=name, font=("SF Pro", 10), text_color="#8b949e")
            lbl.pack(anchor="w", padx=8, pady=(6, 0))

            val_lbl = ctk.CTkLabel(card, text="--", font=("SF Pro", 16, "bold"), text_color="#2fa572")
            val_lbl.pack(anchor="w", padx=8, pady=(0, 0))

            unit_lbl = ctk.CTkLabel(card, text=unit, font=("SF Pro", 9), text_color="#555f6d")
            unit_lbl.pack(anchor="w", padx=8, pady=(0, 6))

            self.cards[m_id] = (card, val_lbl)

        self._current_metric_keys = [item["id"] for item in metric_items]

    def update_telemetry(self, telemetry_data: dict):
        """Updates live measurement card values at 60 FPS."""
        metric_items = telemetry_data.get("metrics", [])
        
        # Check if the set of metrics changed
        keys = [item["id"] for item in metric_items]
        if keys != self._current_metric_keys:
            if keys:
                self._rebuild_cards(metric_items)
            else:
                for card_frame, _ in self.cards.values():
                    card_frame.destroy()
                self.cards.clear()
                self._current_metric_keys.clear()
                if not self.placeholder_lbl.winfo_ismapped():
                    self.placeholder_lbl.pack(expand=True, pady=16)

        # Update values
        for item in metric_items:
            m_id = item["id"]
            if m_id in self.cards:
                _, val_lbl = self.cards[m_id]
                val_lbl.configure(text=str(item.get("value", "--")))

        # Update status
        if telemetry_data.get("is_paused"):
            self.status_badge.configure(text="❚❚ PAUSED", text_color="#e67e22")
        else:
            self.status_badge.configure(text="● 60 FPS", text_color="#2fa572")
