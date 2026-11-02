"""
AI Agent Module for Universal AI Simulation Environment.
Connects directly to LLM with structured tools for scientific experimentation.
Enforces concise engineering reporting (no chatbot essays) and pauses apparatus at t=0.0s.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError

SIMULATION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_wedge",
            "description": "Creates a solid triangular incline wedge apparatus resting flat on the ground floor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique identifier (e.g. 'wedge_30')."},
                    "x_left": {"type": "number", "description": "Left base coordinate (e.g. 80)."},
                    "x_right": {"type": "number", "description": "Right base coordinate (e.g. 520)."},
                    "height": {"type": "number", "description": "Height in pixels. For 30°: (x_right - x_left) * 0.577. For 45°: (x_right - x_left)."},
                    "friction": {"type": "number", "description": "Surface friction coefficient (0.0 to 1.0)."},
                    "elasticity": {"type": "number", "description": "Bounciness (0.0 to 1.0)."}
                },
                "required": ["name", "x_left", "x_right", "height"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_box",
            "description": "Creates a rectangular rigid body (e.g. wooden block, slider).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique identifier."},
                    "x": {"type": "number", "description": "X coordinate."},
                    "y": {"type": "number", "description": "Y coordinate."},
                    "width": {"type": "number", "description": "Width in pixels."},
                    "height": {"type": "number", "description": "Height in pixels."},
                    "mass": {"type": "number", "description": "Mass in kg."},
                    "elasticity": {"type": "number", "description": "Elasticity (0.0 to 1.0)."},
                    "friction": {"type": "number", "description": "Friction coefficient (0.0 to 1.0)."},
                    "static": {"type": "boolean", "description": "If true, object is fixed."},
                    "on_wedge": {
                        "type": "string",
                        "description": "Name of an inclined wedge to automatically place this box on top of, oriented at the slope angle."
                    },
                    "color_rgb": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "[R, G, B] color (0-255)."
                    }
                },
                "required": ["name", "width", "height"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_circle",
            "description": "Creates a circular rigid body (e.g. sphere, pendulum bob, wheel).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique identifier."},
                    "x": {"type": "number", "description": "Center X."},
                    "y": {"type": "number", "description": "Center Y."},
                    "radius": {"type": "number", "description": "Radius in pixels."},
                    "mass": {"type": "number", "description": "Mass in kg."},
                    "elasticity": {"type": "number", "description": "Elasticity (0.0 to 1.0)."},
                    "friction": {"type": "number", "description": "Friction coefficient."},
                    "static": {"type": "boolean", "description": "If true, circle is immovable."},
                    "on_wedge": {
                        "type": "string",
                        "description": "Name of an inclined wedge to place this circle on top of."
                    },
                    "color_rgb": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "[R, G, B] color."
                    }
                },
                "required": ["name", "radius"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_joint",
            "description": "Connects two objects with a pin/pivot joint.",
            "parameters": {
                "type": "object",
                "properties": {
                    "joint_type": {"type": "string", "enum": ["pin"]},
                    "name": {"type": "string", "description": "Unique joint name."},
                    "body_a": {"type": "string", "description": "Name of first body or 'world'."},
                    "body_b": {"type": "string", "description": "Name of second body."}
                },
                "required": ["joint_type", "name", "body_a", "body_b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "apply_force",
            "description": "Applies an impulse force to launch or push a dynamic body.",
            "parameters": {
                "type": "object",
                "properties": {
                    "body_name": {"type": "string", "description": "Name of target body."},
                    "impulse_x": {"type": "number", "description": "Horizontal impulse force."},
                    "impulse_y": {"type": "number", "description": "Vertical impulse force (- is upwards)."}
                },
                "required": ["body_name", "impulse_x", "impulse_y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_experiment_metrics",
            "description": "Configures the real-time telemetry panel with 2 to 5 scientific variables.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "unit": {"type": "string"},
                                "type": {"type": "string", "enum": ["constant", "velocity", "accel", "normal_force"]},
                                "target_body": {"type": "string"},
                                "value": {"type": "number"}
                            },
                            "required": ["id", "name", "unit", "type"]
                        }
                    }
                },
                "required": ["metrics"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clear_world",
            "description": "Clears and resets the simulation canvas to an empty state.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

SYSTEM_PROMPT = """You are the AI Scientific Experimentation Controller for an interactive physics simulation lab (SDG 9).
Canvas: 760 px wide, 480 px high. Ground floor is at y = 460.

CRITICAL INSTRUCTIONS:
1. When asked to simulate an inclined plane, use `create_wedge` (solid triangle resting on floor), and place the sliding block using `on_wedge="<wedge_name>"`.
2. Always call `set_experiment_metrics` to track 2-5 relevant physical quantities.
3. CONVERSATIONAL STYLE:
   - DO NOT write multi-paragraph textbook essays.
   - DO NOT output ASCII art or long equation derivations.
   - Format response strictly as a concise 3-line Experiment Protocol:
     • Setup: [Summary of mass, geometry, and friction]
     • Theoretical Benchmark: [Formula and expected theoretical value, e.g. a_theor = 1.93 m/s²]
     • Status: Apparatus frozen at t=0.0s. Click Release to run experiment.
"""

class AIAgent:
    def __init__(self, physics_engine, api_key: Optional[str] = None, model: str = "gpt-4o-mini", base_url: Optional[str] = None):
        self.engine = physics_engine
        self.api_key = (api_key or os.environ.get("OPENAI_API_KEY", "")).strip()
        self.model = model
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "")).strip()
        self.client: Optional[OpenAI] = None
        self.conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self._init_client()

    def set_api_key(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key.strip()
        if base_url is not None:
            self.base_url = base_url.strip()
        self._init_client()

    def set_model(self, model: str):
        self.model = model

    def _init_client(self):
        if self.api_key:
            try:
                kwargs = {"api_key": self.api_key}
                if self.base_url and self.base_url.strip():
                    kwargs["base_url"] = self.base_url.strip()
                self.client = OpenAI(**kwargs)
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.client = None
        else:
            self.client = None

    @property
    def is_online(self) -> bool:
        return self.client is not None and bool(self.api_key)

    def execute_tool_call(self, function_name: str, args: Dict[str, Any]) -> str:
        """Executes a parsed tool call against the Pymunk physics engine."""
        try:
            if function_name == "create_wedge":
                name = args.get("name", "incline_wedge")
                x_left = float(args.get("x_left", 80))
                x_right = float(args.get("x_right", 500))
                height = float(args.get("height", 220))
                f = float(args.get("friction", 0.5))
                e = float(args.get("elasticity", 0.2))
                self.engine.add_wedge(name, x_left, x_right, height, f, e)
                return f"Constructed solid wedge '{name}' (base {x_left} to {x_right}, height {height}px, μ={f})"

            elif function_name == "create_box":
                name = args.get("name", f"box_{len(self.engine.named_bodies)}")
                x = float(args.get("x", 200))
                y = float(args.get("y", 200))
                w = float(args["width"])
                h = float(args["height"])
                m = float(args.get("mass", 5.0))
                e = float(args.get("elasticity", 0.2))
                f = float(args.get("friction", 0.5))
                s = bool(args.get("static", False))
                on_wedge = args.get("on_wedge")
                color = tuple(args.get("color_rgb", [46, 204, 113]))
                self.engine.add_box(name, x, y, w, h, m, e, f, s, color, on_wedge=on_wedge)
                return f"Placed box '{name}' (mass {m}kg, μ={f})" + (f" on {on_wedge}" if on_wedge else "")

            elif function_name == "create_circle":
                name = args.get("name", f"circle_{len(self.engine.named_bodies)}")
                x = float(args.get("x", 200))
                y = float(args.get("y", 200))
                r = float(args["radius"])
                m = float(args.get("mass", 3.0))
                e = float(args.get("elasticity", 0.8))
                f = float(args.get("friction", 0.2))
                s = bool(args.get("static", False))
                on_wedge = args.get("on_wedge")
                color = tuple(args.get("color_rgb", [52, 152, 219]))
                self.engine.add_circle(name, x, y, r, m, e, f, s, color, on_wedge=on_wedge)
                return f"Placed sphere '{name}' (mass {m}kg)" + (f" on {on_wedge}" if on_wedge else "")

            elif function_name == "create_joint":
                name = args.get("name", f"joint_{len(self.engine.named_joints)}")
                ba = args["body_a"]
                bb = args["body_b"]
                self.engine.add_pin_joint(name, ba, bb)
                return f"Connected pin joint '{name}' between {ba} and {bb}"

            elif function_name == "apply_force":
                bname = args["body_name"]
                fx = float(args["impulse_x"])
                fy = float(args["impulse_y"])
                self.engine.apply_impulse(bname, (fx, fy))
                return f"Applied impulse ({fx}, {fy}) to '{bname}'"

            elif function_name == "set_experiment_metrics":
                metrics = args.get("metrics", [])
                self.engine.set_monitored_metrics(metrics)
                return f"Configured {len(metrics)} telemetry variables."

            elif function_name == "clear_world":
                self.engine.reset()
                return "Cleared world."

            return f"Unknown tool: {function_name}"
        except Exception as e:
            return f"Error executing {function_name}: {e}"

    def process_message(self, user_text: str) -> Tuple[str, List[str]]:
        """Processes user instructions, sets up the experiment, and pauses at t=0."""
        if not self.is_online:
            return (
                "⚠️ API Not Configured.\n\n"
                "Please click '⚙ Settings' at the bottom-left to set your OpenAI key or local Ollama URL.",
                []
            )

        actions_taken = []
        self.conversation_history.append({"role": "user", "content": user_text})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=SIMULATION_TOOLS,
                tool_choice="auto",
                temperature=0.2
            )
            msg = response.choices[0].message
            
            if msg.tool_calls:
                self.conversation_history.append(msg)
                
                for tool_call in msg.tool_calls:
                    fname = tool_call.function.name
                    fargs = json.loads(tool_call.function.arguments)
                    result_msg = self.execute_tool_call(fname, fargs)
                    actions_taken.append(result_msg)
                    
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": fname,
                        "content": result_msg
                    })
                
                # Freeze apparatus at t=0 and save initial snapshot
                self.engine.capture_initial_snapshot()
                
                # Request crisp engineering protocol
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    temperature=0.3
                )
                
                explanation = second_response.choices[0].message.content or ""
                if not explanation.strip():
                    reasoning = getattr(second_response.choices[0].message, "reasoning", "")
                    if reasoning:
                        paragraphs = [p.strip() for p in reasoning.strip().split("\n\n") if p.strip()]
                        explanation = paragraphs[-1] if paragraphs else "Apparatus configured."
                    else:
                        explanation = "Apparatus ready and frozen at t=0.0s."
                
                self.conversation_history.append({"role": "assistant", "content": explanation})
                return explanation, actions_taken
            else:
                explanation = msg.content or ""
                if not explanation.strip():
                    reasoning = getattr(msg, "reasoning", "")
                    if reasoning:
                        paragraphs = [p.strip() for p in reasoning.strip().split("\n\n") if p.strip()]
                        explanation = paragraphs[-1] if paragraphs else "Acknowledged."
                    else:
                        explanation = "Acknowledged."
                self.conversation_history.append({"role": "assistant", "content": explanation})
                return explanation, actions_taken

        except RateLimitError:
            return "⚠️ OpenAI Quota Exceeded (429): Please check billing credits at platform.openai.com.", []
        except AuthenticationError as e:
            return f"⚠️ OpenAI Auth Error (401): {e}", []
        except APIConnectionError as e:
            return f"⚠️ Connection Error: {e}", []
        except Exception as e:
            return f"⚠️ Error: {type(e).__name__} - {e}", []
