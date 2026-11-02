"""
Real-Time Statistics and Measurements Panel (SDG 9 Infrastructure & Telemetry).
Renders real-time scientific telemetry: Kinetic/Potential energy, velocity, and conservation stats.
"""

import customtkinter as ctk

class StatsPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=12, fg_color="#131722", **kwargs)
        
        # Header title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=14, pady=(10, 6))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ REAL-TIME STATISTICS & MEASUREMENTS",
            font=("SF Pro", 12, "bold"),
            text_color="#8b949e"
        )
        title_label.pack(side="left")
        
        self.status_badge = ctk.CTkLabel(
            header_frame,
            text="● SIMULATING",
            font=("SF Pro", 11, "bold"),
            text_color="#2fa572"
        )
        self.status_badge.pack(side="right")

        # Metrics grid container
        self.metrics_container = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.metrics_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 4 Telemetry Cards
        self.card_objects = self._create_card(self.metrics_container, 0, "Active Bodies", "0", "units")
        self.card_ke = self._create_card(self.metrics_container, 1, "Kinetic Energy (Ek)", "0.00", "Joules")
        self.card_pe = self._create_card(self.metrics_container, 2, "Potential Energy (Ep)", "0.00", "Joules")
        self.card_total = self._create_card(self.metrics_container, 3, "Total Mechanical (E)", "0.00", "Joules")

    def _create_card(self, parent, col: int, label_text: str, default_val: str, unit_text: str):
        card = ctk.CTkFrame(parent, fg_color="#1c212d", corner_radius=8, border_width=1, border_color="#262c3d")
        card.grid(row=0, column=col, padx=5, pady=4, sticky="nsew")
        
        lbl = ctk.CTkLabel(card, text=label_text, font=("SF Pro", 10), text_color="#8b949e")
        lbl.pack(anchor="w", padx=8, pady=(6, 0))
        
        val_lbl = ctk.CTkLabel(card, text=default_val, font=("SF Pro", 16, "bold"), text_color="#2fa572")
        val_lbl.pack(anchor="w", padx=8, pady=(0, 0))
        
        unit_lbl = ctk.CTkLabel(card, text=unit_text, font=("SF Pro", 9), text_color="#555f6d")
        unit_lbl.pack(anchor="w", padx=8, pady=(0, 6))
        
        return val_lbl

    def update_telemetry(self, data: dict):
        """Updates the statistics cards from physics engine telemetry."""
        self.card_objects.configure(text=str(data.get("active_objects", 0)))
        self.card_ke.configure(text=f"{data.get('kinetic_energy_j', 0.0):.2f}")
        self.card_pe.configure(text=f"{data.get('potential_energy_j', 0.0):.2f}")
        self.card_total.configure(text=f"{data.get('total_energy_j', 0.0):.2f}")
        
        if data.get("is_paused"):
            self.status_badge.configure(text="❚❚ PAUSED", text_color="#e67e22")
        else:
            self.status_badge.configure(text="● 60 FPS", text_color="#2fa572")
