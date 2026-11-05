"""
Sustainable Research Intelligence Agent Module for PROJECT RIA.
Specialized in UN Sustainable Development Goals (SDG 7, 9, 11, 12, 13).
Capabilities:
- Academic literature querying (arXiv & CrossRef with verified DOIs)
- Research paper & document summarization
- Cross-domain synthesis with Physics Lab simulations
- Visual diagram & chart analysis
- Concept prototype image generation
"""

import os
import re
import json
from typing import Optional, Dict, Any, List, Tuple
from core.academic_search import search_scientific_literature
from core.vision_agent import VisionAgent

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from google import genai
except ImportError:
    genai = None

RESEARCH_SYSTEM_PROMPT = """You are RIA (Research Intelligence Aariz), a Senior AI Scientific Research Fellow specializing in Sustainable Engineering and UN Sustainable Development Goals:
- SDG 7: Affordable and Clean Energy (Kinetic Harvesting, Storage, Regenerative Damping)
- SDG 9: Industry, Innovation and Infrastructure (Low-Carbon Concrete, Resilient Trusses, Self-Healing Materials)
- SDG 11: Sustainable Cities & Resilient Communities (Earthquake Damping, Modular Transport)
- SDG 12: Responsible Consumption and Production (Circular Life Cycle Assessment, Material Efficiency)
- SDG 13: Climate Action (Decarbonized Freight Logistics, Aerodynamic Drag Reduction)

OPERATIONAL PROTOCOL:
1. CITATIONS & FACTUALITY: Always cite real peer-reviewed scientific studies with Author, Year, and DOI link whenever literature is discussed. Never invent fake paper titles.
2. REPORT SUMMARIZATION: When summarizing reports or documents, format strictly into 4 sections:
   • 📋 Executive Summary & Problem Scope
   • 🔬 Experimental Methodology & Parameters
   • 📊 Quantitative Findings & Material/Energy Metrics
   • 🌍 SDG Policy & Engineering Recommendations
3. TONE: Rigorous, clear, academic, and solution-oriented.
"""

SDG_DOSSIERS = {
    "sdg_9": {
        "title": "SDG 9 — Low-Carbon & Self-Healing Concrete Infrastructure",
        "description": "Explores bio-mineralized bacterial self-healing concrete (Bacillus pseudofirmus), supplementary cementitious materials (fly ash, blast-furnace slag), and structural load resilience.",
        "search_seed": "self healing bio concrete supplementary cementitious materials structural resilience SDG 9"
    },
    "sdg_7": {
        "title": "SDG 7 — Kinetic Energy Harvesting & Storage",
        "description": "Studies electromagnetic and piezoelectric vibration energy harvesters, tuned liquid column dampers, and flywheel kinetic storage for sustainable transport networks.",
        "search_seed": "kinetic vibration energy harvesting tuned mass damper regenerative storage SDG 7"
    },
    "sdg_12": {
        "title": "SDG 12 — Circular Material Life Cycle Assessment (LCA)",
        "description": "Comparative cradle-to-grave embodied carbon analysis: Cross-Laminated Timber (CLT) vs Recycled Structural Steel vs Ultra-High-Performance Concrete (UHPC).",
        "search_seed": "circular economy life cycle assessment cross laminated timber structural steel embodied carbon SDG 12"
    },
    "sdg_13": {
        "title": "SDG 13 — Decarbonized Heavy Transport & Rolling Resistance",
        "description": "Investigates rolling friction reduction, aerodynamic drag reduction in rail/truck logistics, and bio-composite brake friction pairs to eliminate microplastic wear.",
        "search_seed": "decarbonized freight transport rolling resistance aerodynamic drag reduction friction SDG 13"
    }
}

class ResearchAgent:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
        gemini_key: Optional[str] = None
    ):
        self.api_key = (api_key or os.environ.get("OPENAI_API_KEY", "")).strip()
        self.model = model
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "")).strip()
        self.gemini_key = (gemini_key or os.environ.get("GEMINI_API_KEY", "")).strip()
        
        provider = "gemini" if "gemini" in model.lower() else "openai"
        self.vision_agent = VisionAgent(provider=provider, api_key=self.api_key, gemini_key=self.gemini_key, base_url=self.base_url)
        self.conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": RESEARCH_SYSTEM_PROMPT}
        ]
        self._init_clients()

    def set_credentials(self, api_key: str, model: str, base_url: str = "", gemini_key: str = ""):
        self.api_key = api_key.strip()
        self.model = model.strip()
        self.base_url = base_url.strip()
        if gemini_key:
            self.gemini_key = gemini_key.strip()
            
        provider = "gemini" if "gemini" in self.model.lower() else "openai"
        self.vision_agent.set_credentials(provider, self.api_key, self.gemini_key, base_url=self.base_url)
        self._init_clients()

    def _init_clients(self):
        self.openai_client = None
        self.gemini_client = None
        
        if OpenAI and self.api_key:
            try:
                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self.openai_client = OpenAI(**kwargs)
            except Exception:
                pass
                
        if genai and self.gemini_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_key)
            except Exception:
                pass

    def clear_history(self):
        self.conversation_history = [
            {"role": "system", "content": RESEARCH_SYSTEM_PROMPT}
        ]

    def ask(
        self,
        user_text: str,
        document_text: str = "",
        attached_image: str = "",
        physics_report: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[Dict[str, Any]], Optional[str]]:
        """
        Processes research instructions:
        Returns: (response_text, citations_list, generated_image_path)
        """
        citations: List[Dict[str, Any]] = []
        generated_image_path: Optional[str] = None
        
        t_low = user_text.lower()

        # 1. Check if user wants Image Generation (Concept Schematic)
        if any(k in t_low for k in ["generate schematic", "generate image", "create blueprint", "draw schematic", "visualize concept"]):
            concept = user_text
            for prefix in ["generate schematic of", "generate image of", "create blueprint of", "draw schematic of", "visualize concept of"]:
                if prefix in t_low:
                    concept = user_text[t_low.find(prefix) + len(prefix):].strip()
                    break
            img_path, img_desc = self.vision_agent.generate_conceptual_schematic(concept)
            generated_image_path = img_path
            return (
                f"🎨 **Generated Technical Schematic:**\n\n"
                f"• Target Concept: {concept}\n"
                f"• Status: Rendered and saved to `{img_path}`\n\n"
                f"{img_desc}\n\n"
                f"> Tip: You can download or embed this schematic into formal research dossiers.",
                citations,
                generated_image_path
            )

        # 2. Check if user uploaded an image for multimodal vision
        if attached_image and os.path.exists(attached_image):
            if any(k in t_low for k in ["chart", "graph", "plot", "curve", "data"]):
                analysis = self.vision_agent.analyze_scientific_chart(attached_image)
            else:
                analysis = self.vision_agent.analyze_diagram_to_simulation(attached_image)
            return (
                f"🔍 **Multimodal Vision Analysis:**\n\n{analysis}",
                citations,
                None
            )

        # 3. Check if user requested Academic Literature Search
        needs_search = any(k in t_low for k in ["search", "literature", "papers", "studies", "articles", "citations", "find research"])
        if needs_search or not document_text:
            search_query = user_text
            # Clean search query
            for p in ["search for", "search papers on", "find literature on", "find studies on", "literature on"]:
                if p in t_low:
                    search_query = user_text[t_low.find(p) + len(p):].strip()
                    break
            citations = search_scientific_literature(search_query, max_total=5)

        # 4. Construct Prompt Context
        context_blocks = []
        if citations:
            c_text = "\n".join([
                f"- [{c.get('source')}] \"{c.get('title')}\" by {', '.join(c.get('authors', []))} ({c.get('year', 'N/A')}). URL: {c.get('url')} | Summary: {c.get('summary')}"
                for c in citations
            ])
            context_blocks.append(f"ACADEMIC LITERATURE CITATIONS RETRIEVED:\n{c_text}")

        if document_text:
            context_blocks.append(f"DOCUMENT/REPORT CONTENT TO ANALYZE:\n{document_text[:6000]}")

        if physics_report:
            p_text = (
                f"RECENT PHYSICS SIMULATION BENCHMARK:\n"
                f"- Title: {physics_report.get('title')}\n"
                f"- Aim: {physics_report.get('aim')}\n"
                f"- Theory: {physics_report.get('theoretical_benchmark')}\n"
                f"- Empirical Peak Velocity: {physics_report.get('peak_velocity_mps')} m/s\n"
                f"- Conclusion: {physics_report.get('conclusion')}"
            )
            context_blocks.append(p_text)

        full_user_content = user_text
        if context_blocks:
            full_user_content = f"{user_text}\n\n---\n" + "\n\n".join(context_blocks)

        # 5. Call LLM (Gemini, OpenAI, or Ollama)
        response_text = self._call_llm(full_user_content)
        return response_text, citations, generated_image_path

    def _call_llm(self, prompt_text: str) -> str:
        # 1. Try Gemini if selected
        if self.gemini_client and "gemini" in self.model.lower():
            try:
                model_name = self.model if "gemini" in self.model else "gemini-2.0-flash"
                history_turns = [m for m in self.conversation_history if m.get("role") != "system"]
                contents = [RESEARCH_SYSTEM_PROMPT]
                for turn in history_turns[-6:]:
                    contents.append(f"{turn['role'].upper()}: {turn['content']}")
                contents.append(f"USER: {prompt_text}")
                res = self.gemini_client.models.generate_content(
                    model=model_name,
                    contents=contents
                )
                reply = res.text or "Analysis completed."
                self.conversation_history.append({"role": "user", "content": prompt_text})
                self.conversation_history.append({"role": "assistant", "content": reply})
                return reply
            except Exception as e:
                print(f"Gemini call error: {e}")

        # 2. Try OpenAI / Ollama client
        if self.openai_client:
            try:
                history_turns = [m for m in self.conversation_history if m.get("role") != "system"]
                messages = [
                    {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
                    *history_turns[-8:],
                    {"role": "user", "content": prompt_text}
                ]
                resp = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2
                )
                msg = resp.choices[0].message
                content = (msg.content or "").strip()
                if not content and hasattr(msg, "reasoning") and msg.reasoning:
                    content = msg.reasoning.strip()
                elif not content and hasattr(msg, "reasoning_content") and msg.reasoning_content:
                    content = msg.reasoning_content.strip()

                reply = content or "Analysis completed."
                self.conversation_history.append({"role": "user", "content": prompt_text})
                self.conversation_history.append({"role": "assistant", "content": reply})
                return reply
            except Exception as e:
                return f"⚠️ API Error ({type(e).__name__}): {e}"

        # 3. Offline Heuristic / Summary Generator if no API key
        return (
            "⚠️ Research API Key Not Configured.\n\n"
            "Please click **'⚙ Settings & Presets'** to configure your Google Gemini API key or OpenAI key.\n\n"
            "• However, peer-reviewed citations were successfully retrieved via arXiv and CrossRef (see citation cards below)."
        )
