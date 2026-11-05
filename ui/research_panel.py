"""
Sustainable Research Intelligence Workspace Panel for PROJECT RIA.
Provides:
- Document & Report Ingestion (Upload, Paste, Summarize)
- 1-Click SDG Research Dossiers (SDG 7, 9, 12, 13)
- Bridge synthesis with Physics Simulation data
- Live Academic Citation Cards (arXiv & CrossRef)
- Multimodal Vision (upload charts/diagrams) and Conceptual Schematic Generation
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Optional, Dict, Any, List
from PIL import Image, ImageTk

from core.research_agent import ResearchAgent, SDG_DOSSIERS

class ResearchPanel(ctk.CTkFrame):
    def __init__(self, master, research_agent: ResearchAgent, get_physics_report_callback=None, **kwargs):
        super().__init__(master, fg_color="#050d1e", **kwargs)
        self.agent = research_agent
        self.get_physics_report = get_physics_report_callback
        
        self.loaded_document_text = ""
        self.loaded_document_name = ""
        self.attached_image_path = ""
        self._image_references = []
        
        self._build_layout()

    def _build_layout(self):
        # 32% Left Sidebar (Ingestion, Dossiers, Actions)
        self.left_sidebar = ctk.CTkFrame(self, fg_color="#0e1117", corner_radius=10, border_width=1, border_color="#1c212d")
        self.left_sidebar.place(relx=0.01, rely=0.015, relwidth=0.32, relheight=0.97)

        # 66% Right Main Panel (Scholarly Chat, Citations, Vision)
        self.right_main = ctk.CTkFrame(self, fg_color="#0e1117", corner_radius=10, border_width=1, border_color="#1c212d")
        self.right_main.place(relx=0.34, rely=0.015, relwidth=0.65, relheight=0.97)

        self._build_sidebar()
        self._build_chat_panel()

    def _build_sidebar(self):
        # Header
        top_bar = ctk.CTkFrame(self.left_sidebar, fg_color="transparent")
        top_bar.pack(fill="x", padx=12, pady=(12, 6))
        
        lbl = ctk.CTkLabel(
            top_bar,
            text="📑 RESEARCH DOSSIERS & INGESTION",
            font=("SF Pro", 11, "bold"),
            text_color="#8b949e"
        )
        lbl.pack(side="left")

        # Ingestion Buttons Frame
        btn_frame = ctk.CTkFrame(self.left_sidebar, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=4)

        self.btn_upload = ctk.CTkButton(
            btn_frame,
            text="📄 Upload Report",
            font=("SF Pro", 11, "bold"),
            fg_color="#1c212d",
            hover_color="#2fa572",
            height=28,
            corner_radius=6,
            command=self._on_upload_report
        )
        self.btn_upload.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_paste = ctk.CTkButton(
            btn_frame,
            text="📋 Paste Text",
            font=("SF Pro", 11),
            fg_color="#1c212d",
            hover_color="#3d4455",
            height=28,
            corner_radius=6,
            command=self._on_paste_text_dialog
        )
        self.btn_paste.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Loaded Document Card
        self.doc_card = ctk.CTkFrame(self.left_sidebar, fg_color="#161b22", corner_radius=6, border_width=1, border_color="#21262d")
        self.doc_card.pack(fill="x", padx=10, pady=6)
        
        self.doc_title_lbl = ctk.CTkLabel(
            self.doc_card,
            text="No document loaded",
            font=("SF Pro", 10, "bold"),
            text_color="#8b949e"
        )
        self.doc_title_lbl.pack(anchor="w", padx=8, pady=(4, 1))
        
        self.doc_info_lbl = ctk.CTkLabel(
            self.doc_card,
            text="Upload .pdf, .txt, or paste an academic paper.",
            font=("SF Pro", 9),
            text_color="#555f6d"
        )
        self.doc_info_lbl.pack(anchor="w", padx=8, pady=(0, 4))

        # SDG Dossiers Section
        ctk.CTkLabel(
            self.left_sidebar,
            text="🌍 1-CLICK SDG RESEARCH DOSSIERS",
            font=("SF Pro", 10, "bold"),
            text_color="#8b949e"
        ).pack(anchor="w", padx=12, pady=(10, 4))

        dossier_box = ctk.CTkFrame(self.left_sidebar, fg_color="transparent")
        dossier_box.pack(fill="x", padx=10, pady=2)

        for key, data in SDG_DOSSIERS.items():
            btn = ctk.CTkButton(
                dossier_box,
                text=data["title"],
                font=("SF Pro", 10),
                fg_color="#1c212d",
                hover_color="#21352e",
                anchor="w",
                height=28,
                corner_radius=6,
                command=lambda k=key: self._on_load_dossier(k)
            )
            btn.pack(fill="x", pady=2)

        # Cross-Domain Physics Bridge Section
        ctk.CTkLabel(
            self.left_sidebar,
            text="⚛ CROSS-DOMAIN PHYSICS BRIDGE",
            font=("SF Pro", 10, "bold"),
            text_color="#8b949e"
        ).pack(anchor="w", padx=12, pady=(12, 4))

        self.btn_bridge = ctk.CTkButton(
            self.left_sidebar,
            text="⚛ Synthesize Physics Simulation Data",
            font=("SF Pro", 10, "bold"),
            fg_color="#1f2937",
            text_color="#58a6ff",
            hover_color="#283548",
            height=30,
            corner_radius=6,
            command=self._on_bridge_physics
        )
        self.btn_bridge.pack(fill="x", padx=10, pady=2)

        # Bottom Tools & Export
        bottom_tools = ctk.CTkFrame(self.left_sidebar, fg_color="transparent")
        bottom_tools.pack(fill="x", side="bottom", padx=10, pady=10)

        self.btn_schematic = ctk.CTkButton(
            bottom_tools,
            text="🎨 Generate Concept Schematic",
            font=("SF Pro", 10, "bold"),
            fg_color="#1c212d",
            hover_color="#475569",
            height=28,
            corner_radius=6,
            command=self._on_prompt_schematic
        )
        self.btn_schematic.pack(fill="x", pady=2)

        self.btn_export = ctk.CTkButton(
            bottom_tools,
            text="📥 Export Literature Review (.md)",
            font=("SF Pro", 10, "bold"),
            fg_color="#1c212d",
            hover_color="#2fa572",
            height=28,
            corner_radius=6,
            command=self._on_export_markdown
        )
        self.btn_export.pack(fill="x", pady=2)

    def _build_chat_panel(self):
        # Header
        chat_header = ctk.CTkFrame(self.right_main, fg_color="transparent")
        chat_header.pack(fill="x", padx=14, pady=(12, 6))

        title = ctk.CTkLabel(
            chat_header,
            text="💬 RESEARCH INTELLIGENCE SCHOLARLY PROTOCOL",
            font=("SF Pro", 11, "bold"),
            text_color="#8b949e"
        )
        title.pack(side="left")

        clear_btn = ctk.CTkButton(
            chat_header,
            text="↺ Clear",
            font=("SF Pro", 10),
            fg_color="#1c212d",
            hover_color="#3d4455",
            width=60,
            height=24,
            corner_radius=5,
            command=self._on_clear_chat
        )
        clear_btn.pack(side="right")

        # Scrollable Chat Display
        self.chat_box = ctk.CTkTextbox(
            self.right_main,
            wrap="word",
            state="normal",
            font=("SF Pro", 12),
            fg_color="#080c14",
            text_color="#e6edf3",
            corner_radius=8,
            border_width=1,
            border_color="#1c212d"
        )
        self.chat_box.pack(fill="both", expand=True, padx=12, pady=4)

        # Welcome message
        self.append_message(
            "System",
            "PROJECT RIA — Sustainable Research Intelligence Suite initialized.\n"
            "• Ask any research question, query peer-reviewed literature (arXiv & CrossRef), or summarize reports.\n"
            "• Upload scientific charts or physics sketches via [ 📷 / 📎 ] for multimodal vision analysis.\n"
            "• Generate conceptual prototype blueprints with [ 🎨 Schematic ]."
        )

        # Image Attachment Status Chip
        self.attachment_chip = ctk.CTkFrame(self.right_main, fg_color="#161b22", corner_radius=6)
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

        # Input Bar
        input_frame = ctk.CTkFrame(self.right_main, fg_color="transparent")
        input_frame.pack(fill="x", padx=12, pady=(6, 12))

        # Attach Image Button
        self.btn_attach = ctk.CTkButton(
            input_frame,
            text="📷",
            font=("SF Pro", 13),
            width=36,
            height=34,
            fg_color="#1c212d",
            hover_color="#2fa572",
            corner_radius=6,
            command=self._on_attach_image
        )
        self.btn_attach.pack(side="left", padx=(0, 6))

        # Text input
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask a sustainable research question, search literature, or summarize...",
            font=("SF Pro", 12),
            fg_color="#161b22",
            border_color="#21262d",
            text_color="#ffffff",
            height=34,
            corner_radius=6
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.input_entry.bind("<Return>", lambda e: self._on_send())

        # Send Button
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            font=("SF Pro", 12, "bold"),
            fg_color="#2fa572",
            hover_color="#106a43",
            width=70,
            height=34,
            corner_radius=6,
            command=self._on_send
        )
        self.send_btn.pack(side="right")

    def _on_upload_report(self):
        file_path = filedialog.askopenfilename(
            title="Select Research Document",
            filetypes=[("Documents", "*.txt *.md *.pdf"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            content = ""
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            elif ext == ".pdf":
                # Basic pdf reading if pypdf is installed or fallback
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    content = "\n".join([page.extract_text() or "" for page in reader.pages[:10]])
                except Exception:
                    with open(file_path, "rb") as f:
                        raw = f.read().decode("latin-1", errors="ignore")
                        import re
                        content = " ".join(re.findall(r'[a-zA-Z0-9\.,;\:\(\)\-\s]{4,}', raw))[:4000]

            self.loaded_document_text = content
            self.loaded_document_name = os.path.basename(file_path)
            self.doc_title_lbl.configure(text=f"📄 {self.loaded_document_name}", text_color="#2fa572")
            self.doc_info_lbl.configure(text=f"{len(content):,} characters ingested. Ready to summarize.")
            
            self.append_message(
                "System",
                f"Ingested document '{self.loaded_document_name}' ({len(content):,} chars).\n"
                f"Type 'Summarize this report' or ask specific questions regarding methodology or quantitative metrics."
            )
        except Exception as e:
            messagebox.showerror("Error Reading File", str(e))

    def _on_paste_text_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Paste Research Text or Report")
        dialog.geometry("600x420")
        dialog.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(dialog, text="Paste Research Paper / Abstract / Data:", font=("SF Pro", 12, "bold"))
        lbl.pack(anchor="w", padx=16, pady=(12, 4))
        
        txt = ctk.CTkTextbox(dialog, wrap="word", font=("SF Pro", 11), fg_color="#161b22")
        txt.pack(fill="both", expand=True, padx=16, pady=6)
        
        def save():
            val = txt.get("1.0", "end").strip()
            if val:
                self.loaded_document_text = val
                self.loaded_document_name = "Pasted_Research_Excerpt.txt"
                self.doc_title_lbl.configure(text=f"📋 {self.loaded_document_name}", text_color="#2fa572")
                self.doc_info_lbl.configure(text=f"{len(val):,} characters pasted. Ready for analysis.")
                self.append_message("System", f"Loaded pasted research excerpt ({len(val):,} chars). Ready to analyze.")
            dialog.destroy()
            
        btn = ctk.CTkButton(dialog, text="Ingest Text", fg_color="#2fa572", command=save)
        btn.pack(pady=10)

    def _on_load_dossier(self, dossier_key: str):
        data = SDG_DOSSIERS.get(dossier_key)
        if not data:
            return
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, f"Synthesize academic research on {data['title']} with key peer-reviewed literature.")
        self._on_send()

    def _on_bridge_physics(self):
        if not self.get_physics_report:
            messagebox.showinfo("Physics Bridge", "No physics engine report callback available.")
            return
        report = self.get_physics_report()
        if not report or report.get("title") == "Physics Experiment" and report.get("duration_sec", 0) == 0:
            messagebox.showinfo("Physics Bridge", "No active simulation run recorded yet.\nRun an experiment in the Physics Lab first, then click Bridge!")
            return
            
        self.append_message(
            "System",
            f"⚛ Bridged Physics Experiment Data:\n"
            f"• Title: {report.get('title')}\n"
            f"• Benchmark: {report.get('theoretical_benchmark')}\n"
            f"• Peak Velocity: {report.get('peak_velocity_mps')} m/s | Avg: {report.get('avg_velocity_mps')} m/s\n"
            f"• Conclusion: {report.get('conclusion')}"
        )
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, f"Based on this {report.get('title')} experiment, what sustainable materials or regenerative systems can optimize its performance?")
        self._on_send()

    def _on_prompt_schematic(self):
        dialog = ctk.CTkInputDialog(
            text="Enter engineering prototype concept to visualize:",
            title="Generate Conceptual Blueprint Schematic"
        )
        concept = dialog.get_input()
        if concept and concept.strip():
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, f"Generate schematic of {concept.strip()}")
            self._on_send()

    def _on_attach_image(self):
        file_path = filedialog.askopenfilename(
            title="Attach Chart Screenshot or Diagram",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp"), ("All Files", "*.*")]
        )
        if file_path:
            self.attached_image_path = file_path
            self.attachment_lbl.configure(text=f"📎 Image: {os.path.basename(file_path)}")
            self.attachment_chip.pack(fill="x", padx=12, pady=(0, 4), before=self.input_entry.master)

    def _clear_attachment(self):
        self.attached_image_path = ""
        self.attachment_chip.pack_forget()

    def _on_clear_chat(self):
        self.agent.clear_history()
        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0", "end")
        self.chat_box.configure(state="disabled")
        self.append_message("System", "Research dialogue cleared.")

    def _on_export_markdown(self):
        content = self.chat_box.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Export", "No content to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Literature Review",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Text Files", "*.txt")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("# PROJECT RIA — Sustainable Research Review\n\n")
                    f.write(content)
                messagebox.showinfo("Export Successful", f"Saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def _on_send(self):
        text = self.input_entry.get().strip()
        if not text:
            return
            
        img_to_send = self.attached_image_path
        self._clear_attachment()
        self.input_entry.delete(0, "end")
        self.send_btn.configure(state="disabled", text="Researching...")

        # Append user message
        user_display = text
        if img_to_send:
            user_display += f"\n[Attached Image: {os.path.basename(img_to_send)}]"
        self.append_message("Researcher", user_display)

        def worker():
            physics_rep = self.get_physics_report() if self.get_physics_report else None
            reply, citations, gen_img = self.agent.ask(
                user_text=text,
                document_text=self.loaded_document_text,
                attached_image=img_to_send,
                physics_report=physics_rep
            )
            self.after(0, lambda: self._on_response_ready(reply, citations, gen_img))

        threading.Thread(target=worker, daemon=True).start()

    def _on_response_ready(self, reply: str, citations: List[Dict[str, Any]], gen_img: Optional[str]):
        self.send_btn.configure(state="normal", text="Send")
        self.append_message("Research Intelligence", reply, citations=citations, image_path=gen_img)

    def append_message(self, sender: str, text: str, citations: Optional[List[Dict[str, Any]]] = None, image_path: Optional[str] = None):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", "\n")

        # Sender badge
        if sender == "Researcher":
            self.chat_box.insert("end", f"👤 {sender}:\n", "sender_user")
            self.chat_box.insert("end", f"{text}\n\n", "body_user")
        elif sender == "System":
            self.chat_box.insert("end", f"⚙ {sender}:\n", "sender_system")
            self.chat_box.insert("end", f"{text}\n\n", "body_system")
        else:
            self.chat_box.insert("end", f"🌱 {sender} (RIA):\n", "sender_agent")
            self.chat_box.insert("end", f"{text}\n\n", "body_agent")

        # Render Citations Cards
        if citations:
            self.chat_box.insert("end", "📚 Peer-Reviewed Academic Citations (arXiv & CrossRef):\n", "cite_header")
            for idx, c in enumerate(citations, 1):
                src = c.get("source", "Academic")
                title = c.get("title", "")
                authors = ", ".join(c.get("authors", [])) or "Research Consortium"
                year = c.get("year", "2024")
                url = c.get("url", "")
                
                cite_str = f"  [{idx}] [{src}] {title} — {authors} ({year})\n"
                if url:
                    cite_str += f"      DOI / Direct URL: {url}\n"
                self.chat_box.insert("end", cite_str, "cite_body")
            self.chat_box.insert("end", "\n")

        # Render Inline Image if generated
        if image_path and os.path.exists(image_path):
            try:
                pil_img = Image.open(image_path)
                # Resize for chat viewport
                pil_img.thumbnail((450, 300), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
                self._image_references.append(tk_img)
                
                self.chat_box.image_create("end", image=tk_img)
                self.chat_box.insert("end", f"\n[Saved to: {os.path.basename(image_path)}]\n\n")
            except Exception as e:
                self.chat_box.insert("end", f"[Image could not be rendered inline: {e}]\n\n")

        # Tag styling
        self.chat_box.tag_config("sender_agent", foreground="#2fa572")
        self.chat_box.tag_config("body_agent", foreground="#e6edf3")
        self.chat_box.tag_config("sender_user", foreground="#58a6ff")
        self.chat_box.tag_config("body_user", foreground="#c9d1d9")
        self.chat_box.tag_config("sender_system", foreground="#8b949e")
        self.chat_box.tag_config("body_system", foreground="#8b949e")
        self.chat_box.tag_config("cite_header", foreground="#58a6ff")
        self.chat_box.tag_config("cite_body", foreground="#7ee787")

        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")
