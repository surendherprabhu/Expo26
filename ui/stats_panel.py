"""
Dynamic Real-Time Statistics & Experiment Control Sheet Panel.
Supports two view modes:
1. Live Telemetry: 60 FPS real-time cards of active variables.
2. Control Sheet / Summary Report: Formal scientific report of aim, theory, measured results, and conclusion.
"""

import customtkinter as ctk
from typing import Dict, List, Any, Optional, Callable

class StatsPanel(ctk.CTkFrame):
    def __init__(self, master, on_end_experiment: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, corner_radius=12, fg_color="#131722", **kwargs)
        self.on_end_experiment = on_end_experiment
        self.current_mode = "telemetry"  # 'telemetry' or 'report'
        self.last_report_data: Optional[Dict[str, Any]] = None
        
        # Header title & mode switch
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=14, pady=(8, 4))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="⚡ EXPERIMENT TELEMETRY",
            font=("SF Pro", 12, "bold"),
            text_color="#8b949e"
        )
        self.title_label.pack(side="left")

        # Mode toggle buttons
        btn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        self.btn_telemetry = ctk.CTkButton(
            btn_frame,
            text="Telemetry",
            font=("SF Pro", 10, "bold"),
            fg_color="#2fa572",
            hover_color="#106a43",
            width=70,
            height=22,
            corner_radius=5,
            command=self.show_telemetry_view
        )
        self.btn_telemetry.pack(side="left", padx=2)

        self.btn_report = ctk.CTkButton(
            btn_frame,
            text="Report Sheet",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#2fa572",
            width=85,
            height=22,
            corner_radius=5,
            command=self.show_report_view
        )
        self.btn_report.pack(side="left", padx=2)

        # Status badge
        self.status_badge = ctk.CTkLabel(
            btn_frame,
            text="● FROZEN",
            font=("SF Pro", 10, "bold"),
            text_color="#e67e22"
        )
        self.status_badge.pack(side="left", padx=(8, 0))

        # Main content container
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        # Telemetry container
        self.metrics_container = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.metrics_container.pack(fill="both", expand=True)

        self.placeholder_lbl = ctk.CTkLabel(
            self.metrics_container,
            text="Apparatus ready and frozen at t=0.0s.\nClick '▶ Release / Run' to start data collection.",
            font=("SF Pro", 11),
            text_color="#555f6d"
        )
        self.placeholder_lbl.pack(expand=True, pady=12)

        # Report Sheet container (hidden by default)
        self.report_container = ctk.CTkScrollableFrame(self.content_container, fg_color="#0e1117", corner_radius=8)

        self.cards: Dict[str, Any] = {}
        self._current_metric_keys: List[str] = []

    def show_telemetry_view(self):
        self.current_mode = "telemetry"
        self.title_label.configure(text="⚡ EXPERIMENT TELEMETRY")
        self.btn_telemetry.configure(fg_color="#2fa572")
        self.btn_report.configure(fg_color="#1c212d")
        self.report_container.pack_forget()
        self.metrics_container.pack(fill="both", expand=True)

    def show_report_view(self):
        self.current_mode = "report"
        self.title_label.configure(text="📋 EXPERIMENT CONTROL & REPORT SHEET")
        self.btn_telemetry.configure(fg_color="#1c212d")
        self.btn_report.configure(fg_color="#2fa572")
        self.metrics_container.pack_forget()
        self.report_container.pack(fill="both", expand=True)
        self._render_report()

    def set_report_data(self, report_data: Dict[str, Any]):
        """Sets data for the formal control sheet and switches view to Report."""
        self.last_report_data = report_data
        self.show_report_view()

    def _render_report(self):
        """Builds structured scientific report."""
        for widget in self.report_container.winfo_children():
            widget.destroy()

        if not self.last_report_data:
            ctk.CTkLabel(
                self.report_container,
                text="No completed experiment data recorded yet.\nRun an experiment and click 'End Experiment' to view the control sheet.",
                font=("SF Pro", 11),
                text_color="#8b949e"
            ).pack(expand=True, pady=20)
            return

        d = self.last_report_data
        
        # Title & Aim
        title_box = ctk.CTkFrame(self.report_container, fg_color="transparent")
        title_box.pack(fill="x", padx=6, pady=(4, 2))
        ctk.CTkLabel(title_box, text=d.get("title", "Report"), font=("SF Pro", 12, "bold"), text_color="#2fa572").pack(anchor="w")
        ctk.CTkLabel(title_box, text=f"Aim: {d.get('aim', '')}", font=("SF Pro", 10), text_color="#c9d1d9", wraplength=700).pack(anchor="w")

        # Theoretical Benchmark
        theory_box = ctk.CTkFrame(self.report_container, fg_color="#161b22", corner_radius=6)
        theory_box.pack(fill="x", padx=6, pady=4)
        ctk.CTkLabel(theory_box, text=f"📐 Theoretical Formula: {d.get('theoretical_benchmark', 'N/A')}", font=("SF Pro", 10, "bold"), text_color="#58a6ff").pack(anchor="w", padx=8, pady=4)

        # Measurements Row
        row = ctk.CTkFrame(self.report_container, fg_color="transparent")
        row.pack(fill="x", padx=6, pady=4)
        
        def add_stat(label, val, unit):
            card = ctk.CTkFrame(row, fg_color="#1c212d", corner_radius=6)
            card.pack(side="left", fill="both", expand=True, padx=3)
            ctk.CTkLabel(card, text=label, font=("SF Pro", 9), text_color="#8b949e").pack(anchor="w", padx=6, pady=(3, 0))
            ctk.CTkLabel(card, text=f"{val} {unit}", font=("SF Pro", 12, "bold"), text_color="#2fa572").pack(anchor="w", padx=6, pady=(0, 3))

        add_stat("Duration (t)", d.get("duration_sec", 0.0), "s")
        add_stat("Peak Velocity", d.get("peak_velocity_mps", 0.0), "m/s")
        add_stat("Avg Velocity", d.get("avg_velocity_mps", 0.0), "m/s")
        add_stat("Active Bodies", d.get("active_bodies", 0), "units")

        # Conclusion
        conc_box = ctk.CTkFrame(self.report_container, fg_color="transparent")
        conc_box.pack(fill="x", padx=6, pady=(2, 6))
        ctk.CTkLabel(conc_box, text="Scientific Conclusion:", font=("SF Pro", 10, "bold"), text_color="#8b949e").pack(anchor="w")
        ctk.CTkLabel(conc_box, text=d.get("conclusion", ""), font=("SF Pro", 10), text_color="#e6edf3", wraplength=700).pack(anchor="w")

    def _rebuild_cards(self, metric_items: List[Dict[str, Any]]):
        """Reconstructs dynamic cards using pack(side='left')."""
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
        if self.current_mode != "telemetry":
            return

        metric_items = telemetry_data.get("metrics", [])
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
                    self.placeholder_lbl.pack(expand=True, pady=12)

        for item in metric_items:
            m_id = item["id"]
            if m_id in self.cards:
                _, val_lbl = self.cards[m_id]
                val_lbl.configure(text=str(item.get("value", "--")))

        if telemetry_data.get("is_paused"):
            self.status_badge.configure(text="❚❚ FROZEN (t=0)", text_color="#e67e22")
        else:
            self.status_badge.configure(text="● RUNNING", text_color="#2fa572")
