"""
AI Agent Module for Universal AI Simulation Environment.
Connects directly to OpenAI API using structured tool calling to manipulate Pymunk simulation.
No offline fallback: all NLP is executed directly through the model.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError

# Tool schemas for OpenAI function calling
SIMULATION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_box",
            "description": "Creates a rectangular rigid body (e.g. block, crate, beam, platform).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique identifier for the object."},
                    "x": {"type": "number", "description": "X coordinate in canvas (0 to 750)."},
                    "y": {"type": "number", "description": "Y coordinate in canvas (0 to 450, floor is at y=460)."},
                    "width": {"type": "number", "description": "Width in pixels."},
                    "height": {"type": "number", "description": "Height in pixels."},
                    "mass": {"type": "number", "description": "Mass in kg. Defaults to 5.0."},
                    "elasticity": {"type": "number", "description": "Bounciness from 0.0 to 1.0."},
                    "friction": {"type": "number", "description": "Surface friction coefficient (e.g. 0.1 to 0.9)."},
                    "static": {"type": "boolean", "description": "If true, object is fixed in place."},
                    "on_ramp": {
                        "type": "string",
                        "description": "Name of an inclined ramp (e.g. 'ramp_1') to automatically place this box on top of, oriented at the ramp angle."
                    },
                    "color_rgb": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "[R, G, B] color (0-255)."
                    }
                },
                "required": ["name", "x", "y", "width", "height"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_circle",
            "description": "Creates a circular rigid body (e.g. ball, wheel, cylinder).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique identifier for the circle."},
                    "x": {"type": "number", "description": "Center X coordinate."},
                    "y": {"type": "number", "description": "Center Y coordinate."},
                    "radius": {"type": "number", "description": "Radius in pixels."},
                    "mass": {"type": "number", "description": "Mass in kg."},
                    "elasticity": {"type": "number", "description": "Bounciness from 0.0 to 1.0."},
                    "friction": {"type": "number", "description": "Friction coefficient."},
                    "static": {"type": "boolean", "description": "If true, circle is immovable."},
                    "on_ramp": {
                        "type": "string",
                        "description": "Name of an inclined ramp (e.g. 'ramp_1') to place this circle on top of."
                    },
                    "color_rgb": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "[R, G, B] color."
                    }
                },
                "required": ["name", "x", "y", "radius"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_ramp",
            "description": "Creates an inclined static ramp or plane segment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique identifier for the ramp."},
                    "x1": {"type": "number", "description": "Start X coordinate."},
                    "y1": {"type": "number", "description": "Start Y coordinate."},
                    "x2": {"type": "number", "description": "End X coordinate."},
                    "y2": {"type": "number", "description": "End Y coordinate."},
                    "thickness": {"type": "number", "description": "Thickness in pixels."},
                    "elasticity": {"type": "number", "description": "Bounciness (0.0 to 1.0)."},
                    "friction": {"type": "number", "description": "Friction coefficient (0.0 to 1.0)."}
                },
                "required": ["name", "x1", "y1", "x2", "y2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_joint",
            "description": "Connects two objects with a pin joint (pivot) or damped spring.",
            "parameters": {
                "type": "object",
                "properties": {
                    "joint_type": {"type": "string", "enum": ["pin", "spring"]},
                    "name": {"type": "string", "description": "Unique joint identifier."},
                    "body_a": {"type": "string", "description": "Name of first body or 'world'."},
                    "body_b": {"type": "string", "description": "Name of second body."},
                    "stiffness": {"type": "number", "description": "Spring stiffness."},
                    "rest_length": {"type": "number", "description": "Spring rest length."}
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
            "name": "set_world_gravity",
            "description": "Modifies world gravity vector (e.g. Earth [0, 900], Moon [0, 160], Zero-G [0, 0]).",
            "parameters": {
                "type": "object",
                "properties": {
                    "gx": {"type": "number", "description": "Horizontal gravity."},
                    "gy": {"type": "number", "description": "Vertical gravity."}
                },
                "required": ["gx", "gy"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_experiment_metrics",
            "description": "CRITICAL: Configures the real-time telemetry panel with 2 to 5 scientific variables specifically relevant to this experiment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metrics": {
                        "type": "array",
                        "description": "List of 2 to 5 scientific measurements to display live on screen.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Short identifier (e.g. 'theta', 'mu', 'v_block', 'a_block')."},
                                "name": {"type": "string", "description": "Display title (e.g. 'Incline Angle (θ)', 'Friction Coeff (μ)', 'Velocity (v)', 'Acceleration (a)', 'Normal Force (Fn)')."},
                                "unit": {"type": "string", "description": "Scientific unit (e.g. '°', 'm/s', 'm/s²', 'N', 'kg', 'J')."},
                                "type": {
                                    "type": "string",
                                    "enum": ["constant", "velocity", "accel", "angle", "friction", "mass", "kinetic_energy", "potential_energy", "normal_force"],
                                    "description": "How the telemetry value is computed."
                                },
                                "target_body": {"type": "string", "description": "Name of the target body if measuring velocity, accel, mass, etc."},
                                "value": {"type": "number", "description": "Fixed numeric value if type is constant or angle (e.g. 30.0 for 30 degrees)."}
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

SYSTEM_PROMPT = """You are the AI Physics Controller for an interactive 2D simulation environment (Expo26 / SDG 9 Innovation Lab).
Your canvas is 760 pixels wide and 480 pixels high:
- (0, 0) is top-left.
- Floor is at y = 460.
- Standard gravity is (0, 900).

CORE RULES:
1. When asked to construct a physical system, call the appropriate tools (create_box, create_circle, create_ramp, create_joint, apply_force, set_world_gravity, clear_world).
2. SPATIAL PLACEMENT:
   - When placing a box or sphere on an inclined ramp, always pass `on_ramp="<ramp_name>"`! The physics engine will automatically calculate the slope, tilt the body, and rest it at the top of the ramp.
3. ALWAYS call `set_experiment_metrics` to configure 2 to 5 scientific variables specifically relevant to what you are simulating.
   Example: For an inclined plane with a sliding block:
   - Incline Angle (θ) in ° [constant]
   - Friction Coeff (μ) [constant or friction of ramp]
   - Block Velocity (v) in m/s [velocity of block]
   - Block Acceleration (a) in m/s² [accel of block]
   - Normal Force (Fn) in N [normal_force]
4. Provide concise scientific explanations explaining the observed equations and physical behavior.
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
            if function_name == "create_box":
                name = args.get("name", f"box_{len(self.engine.named_bodies)}")
                x = float(args["x"])
                y = float(args["y"])
                w = float(args["width"])
                h = float(args["height"])
                m = float(args.get("mass", 5.0))
                e = float(args.get("elasticity", 0.6))
                f = float(args.get("friction", 0.7))
                s = bool(args.get("static", False))
                on_ramp = args.get("on_ramp")
                color = tuple(args.get("color_rgb", [46, 204, 113]))
                self.engine.add_box(name, x, y, w, h, m, e, f, s, color, on_ramp=on_ramp)
                return f"Created box '{name}' at ({x}, {y})" + (f" on {on_ramp}" if on_ramp else "")

            elif function_name == "create_circle":
                name = args.get("name", f"circle_{len(self.engine.named_bodies)}")
                x = float(args["x"])
                y = float(args["y"])
                r = float(args["radius"])
                m = float(args.get("mass", 3.0))
                e = float(args.get("elasticity", 0.8))
                f = float(args.get("friction", 0.5))
                s = bool(args.get("static", False))
                on_ramp = args.get("on_ramp")
                color = tuple(args.get("color_rgb", [52, 152, 219]))
                self.engine.add_circle(name, x, y, r, m, e, f, s, color, on_ramp=on_ramp)
                return f"Created circle '{name}' at ({x}, {y})" + (f" on {on_ramp}" if on_ramp else "")

            elif function_name == "create_ramp":
                name = args.get("name", f"ramp_{len(self.engine.named_shapes)}")
                x1 = float(args["x1"])
                y1 = float(args["y1"])
                x2 = float(args["x2"])
                y2 = float(args["y2"])
                t = float(args.get("thickness", 6.0))
                e = float(args.get("elasticity", 0.5))
                f = float(args.get("friction", 0.6))
                self.engine.add_segment(name, x1, y1, x2, y2, t, e, f)
                return f"Created ramp '{name}' from ({x1},{y1}) to ({x2},{y2})"

            elif function_name == "create_joint":
                name = args.get("name", f"joint_{len(self.engine.named_joints)}")
                jtype = args.get("joint_type", "pin")
                ba = args["body_a"]
                bb = args["body_b"]
                if jtype == "spring":
                    length = float(args.get("rest_length", 80.0))
                    k = float(args.get("stiffness", 100.0))
                    self.engine.add_spring_joint(name, ba, bb, length, k)
                else:
                    self.engine.add_pin_joint(name, ba, bb)
                return f"Created {jtype} joint '{name}' between {ba} and {bb}"

            elif function_name == "apply_force":
                bname = args["body_name"]
                fx = float(args["impulse_x"])
                fy = float(args["impulse_y"])
                self.engine.apply_impulse(bname, (fx, fy))
                return f"Applied impulse ({fx}, {fy}) to '{bname}'"

            elif function_name == "set_world_gravity":
                gx = float(args["gx"])
                gy = float(args["gy"])
                self.engine.set_gravity(gx, gy)
                return f"Set gravity to ({gx}, {gy})"

            elif function_name == "set_experiment_metrics":
                metrics = args.get("metrics", [])
                self.engine.set_monitored_metrics(metrics)
                return f"Configured {len(metrics)} dynamic telemetry variables."

            elif function_name == "clear_world":
                self.engine.reset()
                return "Cleared simulation world."

            return f"Unknown tool: {function_name}"
        except Exception as e:
            return f"Error executing {function_name}: {e}"

    def process_message(self, user_text: str) -> Tuple[str, List[str]]:
        """Processes user instructions directly through the LLM."""
        if not self.is_online:
            return (
                "⚠️ API Key Not Configured.\n\n"
                "Please click '⚙ Settings' at the bottom-left to enter your OpenAI API key.",
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
            
            # Handle tool calls
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
                
                # Second turn for natural language explanation
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    temperature=0.4
                )
                explanation = second_response.choices[0].message.content or ""
                if not explanation.strip():
                    reasoning = getattr(second_response.choices[0].message, "reasoning", "")
                    if reasoning:
                        paragraphs = [p.strip() for p in reasoning.strip().split("\n\n") if p.strip()]
                        explanation = paragraphs[-1] if paragraphs else "Simulation updated."
                    else:
                        explanation = "Simulation configured and running."
                
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

        except RateLimitError as e:
            err_msg = (
                "⚠️ OpenAI Rate Limit / Quota Exceeded (429):\n\n"
                "Your account has no remaining credits or exceeded its current quota.\n"
                "Please check your billing and credits at: https://platform.openai.com/settings/organization/billing/"
            )
            return err_msg, []
        except AuthenticationError as e:
            return f"⚠️ OpenAI Authentication Error (401):\n\nInvalid API Key. Please update your key in Settings.\nDetails: {e}", []
        except APIConnectionError as e:
            return f"⚠️ Network Connection Error:\n\nCould not reach OpenAI servers. Please check your internet connection.\nDetails: {e}", []
        except Exception as e:
            return f"⚠️ OpenAI API Error:\n\n{type(e).__name__}: {e}", []
