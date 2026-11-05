"""
Multimodal Vision & Image Generation Engine for PROJECT RIA.
Provides:
1. Vision (Reading images, charts, and apparatus diagrams):
   - Diagram-to-Physics parser (reconstructs physical sketches into Pymunk simulations)
   - Research chart reader (extracts numerical data curves and axes from paper screenshots)
2. Image Generation:
   - OpenAI DALL-E 3
   - Google Gemini Imagen 3
"""

import os
import io
import time
import base64
import urllib.request
from PIL import Image
from typing import Optional, Dict, Any, Tuple

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

IMAGE_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "generated_images")
os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

class VisionAgent:
    def __init__(self, provider: str = "openai", api_key: str = "", gemini_key: str = ""):
        self.provider = provider.lower()
        self.api_key = api_key.strip()
        self.gemini_key = gemini_key.strip()
        self._init_clients()

    def set_credentials(self, provider: str, api_key: str = "", gemini_key: str = ""):
        self.provider = provider.lower()
        if api_key:
            self.api_key = api_key.strip()
        if gemini_key:
            self.gemini_key = gemini_key.strip()
        self._init_clients()

    def _init_clients(self):
        self.openai_client = None
        self.gemini_client = None
        
        if OpenAI and self.api_key:
            try:
                self.openai_client = OpenAI(api_key=self.api_key)
            except Exception:
                pass
                
        if genai and self.gemini_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_key)
            except Exception:
                pass

    def encode_image_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def analyze_diagram_to_simulation(self, image_path: str) -> str:
        """
        Multimodal Vision: Inspects an uploaded diagram/sketch of a physics setup
        and converts it into instructions/parameters for the Pymunk simulation.
        """
        prompt = (
            "You are the Vision Architect for PROJECT RIA physics lab (canvas: 760x480, floor at y=440).\n"
            "Analyze this uploaded diagram or sketch of a physical experiment.\n"
            "1. Identify the components (inclined ramp/wedge, spheres, blocks, pulleys, pendulums).\n"
            "2. Estimate geometry: angles (degrees), dimensions, and positions.\n"
            "3. State how to simulate it in natural language matching our engine: e.g., "
            "'Construct a 30-degree solid wedge on the floor with a 5 kg wooden block resting on it with friction 0.4.'\n"
            "Keep your output crisp, scientific, and ready to execute."
        )
        return self._run_multimodal_vision(image_path, prompt)

    def analyze_scientific_chart(self, image_path: str) -> str:
        """
        Multimodal Vision: Reads a chart/plot from a scientific paper, extracts data points,
        trend lines, and provides engineering insights.
        """
        prompt = (
            "You are RIA's Senior Research Data Analyst.\n"
            "Read this scientific chart/graph from an academic publication.\n"
            "Extract:\n"
            "1. Dependent (Y-axis) and Independent (X-axis) variables with units.\n"
            "2. Observed trend, slope, and critical inflection points.\n"
            "3. Quantitative takeaways (e.g. peak efficiency, yield stress, energy loss).\n"
            "4. Relevance to Sustainable Development Goals (SDG 7, 9, 12, or 13)."
        )
        return self._run_multimodal_vision(image_path, prompt)

    def _run_multimodal_vision(self, image_path: str, user_prompt: str) -> str:
        """Dispatches multimodal vision request to Gemini or OpenAI."""
        if not os.path.exists(image_path):
            return f"⚠️ Error: Image file not found at {image_path}"

        # 1. Try Gemini if configured or primary
        if self.gemini_client and (self.provider == "gemini" or not self.openai_client):
            try:
                pil_img = Image.open(image_path)
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[pil_img, user_prompt]
                )
                return response.text or "Analysis completed."
            except Exception as e:
                print(f"Gemini Vision error: {e}")

        # 2. Try OpenAI Vision (gpt-4o)
        if self.openai_client:
            try:
                b64_img = self.encode_image_base64(image_path)
                # Detect mime type
                ext = os.path.splitext(image_path)[1].lower()
                mime = "image/png" if ext == ".png" else "image/jpeg"
                
                resp = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{mime};base64,{b64_img}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=600
                )
                return resp.choices[0].message.content or "Analysis completed."
            except Exception as e:
                return f"⚠️ OpenAI Vision error: {e}"

        return (
            "⚠️ Vision API Key Required.\n"
            "Please configure your Google Gemini API Key or OpenAI API Key in '⚙ Settings & Presets' to analyze images."
        )

    def generate_conceptual_schematic(self, concept_description: str) -> Tuple[Optional[str], str]:
        """
        Generates a photorealistic/technical conceptual schematic using
        OpenAI DALL-E 3 or Google Imagen 3, saving to disk and returning path.
        """
        timestamp = int(time.time())
        output_filename = f"schematic_{timestamp}.png"
        output_path = os.path.join(IMAGE_CACHE_DIR, output_filename)
        
        refined_prompt = (
            f"Technical conceptual engineering diagram and architectural cross-section of {concept_description}. "
            "Clean blueprint visual, labeled schematic components, sustainable materials, modern laboratory lighting, "
            "photorealistic 4k ISO technical rendering."
        )

        # 1. Try OpenAI DALL-E 3
        if self.openai_client and (self.provider == "openai" or not self.gemini_client):
            try:
                response = self.openai_client.images.generate(
                    model="dall-e-3",
                    prompt=refined_prompt[:950],
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
                img_url = response.data[0].url
                # Download and save
                req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as res:
                    img_data = res.read()
                with open(output_path, "wb") as f:
                    f.write(img_data)
                return output_path, f"Generated concept schematic for: {concept_description}"
            except Exception as e:
                print(f"DALL-E 3 error: {e}")

        # 2. Try Gemini Imagen 3
        if self.gemini_client:
            try:
                result = self.gemini_client.models.generate_images(
                    model="imagen-3.0-generate-002",
                    prompt=refined_prompt[:450],
                    config=dict(number_of_images=1, output_mime_type="image/png")
                )
                for generated_image in result.generated_images:
                    image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                    image.save(output_path)
                    return output_path, f"Generated Imagen 3 concept schematic for: {concept_description}"
            except Exception as e:
                print(f"Gemini Imagen error: {e}")

        # If no key configured, generate a high-contrast procedural SVG/Canvas blueprint preview
        try:
            self._generate_fallback_blueprint(output_path, concept_description)
            return output_path, f"Generated technical concept blueprint (Procedural Schematic) for: {concept_description}"
        except Exception as e:
            return None, f"⚠️ Image generation requires an active OpenAI or Gemini key ({e})."

    def _generate_fallback_blueprint(self, filepath: str, text: str):
        """Generates an aesthetic engineering schematic placeholder with PIL when offline."""
        from PIL import ImageDraw, ImageFont
        img = Image.new("RGBA", (700, 420), (14, 21, 37, 255))
        draw = ImageDraw.Draw(img)
        
        # Grid
        for x in range(0, 700, 25):
            draw.line([(x, 0), (x, 420)], fill=(28, 38, 64, 255), width=1)
        for y in range(0, 420, 25):
            draw.line([(0, y), (700, y)], fill=(28, 38, 64, 255), width=1)
            
        # Border
        draw.rectangle([(15, 15), (685, 405)], outline=(47, 165, 114, 255), width=2)
        
        # Blueprint elements
        draw.text((30, 30), "PROJECT RIA // TECHNICAL CONCEPT SCHEMATIC", fill=(47, 165, 114, 255))
        draw.text((30, 55), f"Target: {text[:65]}...", fill=(200, 215, 230, 255))
        
        # Technical blueprint box & vectors
        draw.rectangle([(180, 130), (520, 310)], outline=(88, 166, 255, 255), width=2)
        draw.line([(180, 130), (520, 310)], fill=(47, 165, 114, 180), width=1)
        draw.line([(180, 310), (520, 130)], fill=(47, 165, 114, 180), width=1)
        draw.ellipse([(320, 190), (380, 250)], outline=(255, 193, 7, 255), width=2)
        
        draw.text((200, 330), "• Finite Element Load Distribution", fill=(140, 160, 180, 255))
        draw.text((200, 350), "• ISO 14040 Life Cycle Assessment Node", fill=(140, 160, 180, 255))
        draw.text((200, 370), "• Regenerative Kinetic Coupling Matrix", fill=(140, 160, 180, 255))
        
        img.save(filepath, "PNG")
