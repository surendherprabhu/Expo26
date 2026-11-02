"""
AI Agent Module for Universal AI Simulation Environment.
Connects to OpenAI API using structured tool calling to manipulate the Pymunk simulation.
Includes offline heuristic fallback for instant offline execution and demo scenes.
"""

import json
import os
from typing import Any, Callable, Dict, List, Optional, Tuple
from openai import OpenAI

# Predefined tool schemas for OpenAI function calling
SIMULATION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_box",
            "description": "Creates a rectangular rigid body (e.g. brick, crate, beam, platform).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique identifier for the object."},
                    "x": {"type": "number", "description": "X coordinate in canvas (0 to 750, 0 is left)."},
                    "y": {"type": "number", "description": "Y coordinate in canvas (0 to 450, 0 is top, 450 is floor)."},
                    "width": {"type": "number", "description": "Width in pixels."},
                    "height": {"type": "number", "description": "Height in pixels."},
                    "mass": {"type": "number", "description": "Mass in kg. Defaults to 5.0."},
                    "elasticity": {"type": "number", "description": "Bounciness from 0.0 (clay) to 1.0 (superball)."},
                    "friction": {"type": "number", "description": "Surface friction from 0.0 to 1.0."},
                    "static": {"type": "boolean", "description": "If true, object is fixed and immovable."},
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
            "description": "Creates a circular rigid body (e.g. ball, wheel, sphere, particle).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique identifier for the circle."},
                    "x": {"type": "number", "description": "Center X coordinate."},
                    "y": {"type": "number", "description": "Center Y coordinate."},
                    "radius": {"type": "number", "description": "Radius in pixels."},
                    "mass": {"type": "number", "description": "Mass in kg. Defaults to 3.0."},
                    "elasticity": {"type": "number", "description": "Bounciness from 0.0 to 1.0."},
                    "friction": {"type": "number", "description": "Friction coefficient."},
                    "static": {"type": "boolean", "description": "If true, circle is immovable."},
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
            "description": "Creates an inclined static ramp, shelf, or barrier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique identifier for the segment."},
                    "x1": {"type": "number", "description": "Start X coordinate."},
                    "y1": {"type": "number", "description": "Start Y coordinate."},
                    "x2": {"type": "number", "description": "End X coordinate."},
                    "y2": {"type": "number", "description": "End Y coordinate."},
                    "thickness": {"type": "number", "description": "Thickness in pixels."},
                    "elasticity": {"type": "number", "description": "Bounciness (0.0 to 1.0)."},
                    "friction": {"type": "number", "description": "Friction (0.0 to 1.0)."}
                },
                "required": ["name", "x1", "y1", "x2", "y2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_joint",
            "description": "Connects two objects with a pin/pivot joint or elastic spring.",
            "parameters": {
                "type": "object",
                "properties": {
                    "joint_type": {"type": "string", "enum": ["pin", "spring"]},
                    "name": {"type": "string", "description": "Unique joint identifier."},
                    "body_a": {"type": "string", "description": "Name of first body or 'world'."},
                    "body_b": {"type": "string", "description": "Name of second body."},
                    "stiffness": {"type": "number", "description": "Spring stiffness (if spring)."},
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
            "description": "Applies an impulse blast/force to push a body.",
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
- (760, 480) is bottom-right.
- The ground floor is at y = 460.
- Normal gravity is (0, 900).

When the user asks you to create, simulate, modify, or experiment with physical systems:
1. Call the appropriate tools (create_box, create_circle, create_ramp, create_joint, apply_force, set_world_gravity, clear_world).
2. Choose logical coordinates and physical properties (mass, friction, elasticity) that ensure physical stability.
3. In your response text, briefly explain the scientific behavior, engineering principles (e.g., kinetic energy, friction, center of mass, structural load), and what to observe.
4. Keep explanations concise, crisp, and informative.
"""

class AIAgent:
    def __init__(self, physics_engine, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.engine = physics_engine
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model
        self.client: Optional[OpenAI] = None
        self.conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self._init_client()

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        self._init_client()

    def set_model(self, model: str):
        self.model = model

    def _init_client(self):
        if self.api_key and self.api_key.strip():
            try:
                self.client = OpenAI(api_key=self.api_key.strip())
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.client = None
        else:
            self.client = None

    @property
    def is_online(self) -> bool:
        return self.client is not None and bool(self.api_key.strip())

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
                color = tuple(args.get("color_rgb", [46, 204, 113]))
                self.engine.add_box(name, x, y, w, h, m, e, f, s, color)
                return f"Created box '{name}' at ({x}, {y})"

            elif function_name == "create_circle":
                name = args.get("name", f"circle_{len(self.engine.named_bodies)}")
                x = float(args["x"])
                y = float(args["y"])
                r = float(args["radius"])
                m = float(args.get("mass", 3.0))
                e = float(args.get("elasticity", 0.8))
                f = float(args.get("friction", 0.5))
                s = bool(args.get("static", False))
                color = tuple(args.get("color_rgb", [52, 152, 219]))
                self.engine.add_circle(name, x, y, r, m, e, f, s, color)
                return f"Created circle '{name}' at ({x}, {y})"

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

            elif function_name == "clear_world":
                self.engine.reset()
                return "Cleared simulation world."

            return f"Unknown tool: {function_name}"
        except Exception as e:
            return f"Error executing {function_name}: {e}"

    def process_message(self, user_text: str) -> Tuple[str, List[str]]:
        """Processes user natural language instruction and returns (explanation, list_of_actions)."""
        actions_taken = []
        
        # If API is not online, use offline smart dispatcher
        if not self.is_online:
            return self._process_offline(user_text)

        # Call OpenAI Chat Completions with function calling
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
                # Add assistant message with tool calls to history
                self.conversation_history.append(msg)
                
                for tool_call in msg.tool_calls:
                    fname = tool_call.function.name
                    fargs = json.loads(tool_call.function.arguments)
                    result_msg = self.execute_tool_call(fname, fargs)
                    actions_taken.append(result_msg)
                    
                    # Add tool response to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": fname,
                        "content": result_msg
                    })
                
                # Request final conversational explanation
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    temperature=0.4
                )
                explanation = second_response.choices[0].message.content or "Simulation updated."
                self.conversation_history.append({"role": "assistant", "content": explanation})
                return explanation, actions_taken
            else:
                explanation = msg.content or "Done."
                self.conversation_history.append({"role": "assistant", "content": explanation})
                return explanation, actions_taken

        except Exception as e:
            print(f"OpenAI API call failed: {e}. Falling back to offline engine.")
            return self._process_offline(user_text)

    def _process_offline(self, text: str) -> Tuple[str, List[str]]:
        """Fallback rule-based simulator for offline use and preset demos."""
        t = text.lower()
        actions = []
        
        if "clear" in t or "reset" in t:
            self.engine.reset()
            return "Simulation reset. Canvas is cleared.", ["Cleared simulation world."]
            
        elif "cradle" in t or "newton" in t:
            self.engine.reset()
            # Spawn Newton's cradle
            y_pivot = 100
            spacing = 38
            r = 18
            for i in range(5):
                name = f"bob_{i}"
                x = 300 + i * spacing
                self.engine.add_circle(name, x, y_pivot + 160, r, mass=4.0, elasticity=0.98, friction=0.05, color=(52, 152, 219))
                # Add pin joint to static anchor
                anchor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
                anchor_body.position = (x, y_pivot)
                self.engine.space.add(anchor_body)
                joint = pymunk.PinJoint(anchor_body, self.engine.named_bodies[name], (0, 0), (0, 0))
                self.engine.space.add(joint)
                actions.append(f"Constructed pendulum bob {i}")
            # Deflect first ball to initiate momentum transfer
            self.engine.apply_impulse("bob_0", (-800, -200))
            actions.append("Displaced first bob to transfer momentum.")
            return "Built a 5-ball Newton's Cradle. Demonstrates conservation of linear momentum ($p=mv$) and near-elastic kinetic energy transfer.", actions

        elif "ramp" in t or "incline" in t:
            self.engine.reset()
            self.engine.add_segment("ramp_main", 60, 160, 460, 360, thickness=8, friction=0.3, elasticity=0.2)
            self.engine.add_circle("rolling_sphere", 100, 120, 20, mass=5.0, friction=0.4, elasticity=0.5, color=(46, 204, 113))
            self.engine.add_box("sliding_crate", 200, 190, 35, 35, mass=8.0, friction=0.8, elasticity=0.1, color=(230, 126, 34))
            actions.extend(["Added inclined ramp segment", "Added rolling sphere", "Added sliding friction crate"])
            return "Constructed an inclined plane with a rolling sphere and a sliding friction box. Demonstrates rotational kinetic energy vs sliding friction.", actions

        elif "bridge" in t or "truss" in t:
            self.engine.reset()
            # Left & Right piers
            self.engine.add_box("pier_left", 140, 380, 80, 140, static=True, color=(100, 110, 120))
            self.engine.add_box("pier_right", 620, 380, 80, 140, static=True, color=(100, 110, 120))
            # Bridge deck segments
            self.engine.add_box("deck_1", 240, 315, 120, 16, mass=10.0, color=(46, 204, 113))
            self.engine.add_box("deck_2", 380, 315, 160, 16, mass=12.0, color=(46, 204, 113))
            self.engine.add_box("deck_3", 520, 315, 120, 16, mass=10.0, color=(46, 204, 113))
            # Joints
            self.engine.add_pin_joint("j_left", "pier_left", "deck_1", (40, -70), (-60, 0))
            self.engine.add_pin_joint("j_mid1", "deck_1", "deck_2", (60, 0), (-80, 0))
            self.engine.add_pin_joint("j_mid2", "deck_2", "deck_3", (80, 0), (-60, 0))
            self.engine.add_pin_joint("j_right", "deck_3", "pier_right", (60, 0), (-40, -70))
            # Heavy test load dropped above
            self.engine.add_circle("load_ball", 380, 100, 30, mass=35.0, color=(231, 76, 60))
            actions.extend(["Erected bridge piers", "Connected 3 bridge deck sections with pin joints", "Dropped 35kg test load on bridge span"])
            return "Built a 3-segment pinned bridge deck spanning a 480px gap with a 35kg test load dropping on the midpoint. Demonstrates structural bending moments and joint reactions (SDG 9 Infrastructure).", actions

        elif "tower" in t or "stack" in t:
            self.engine.reset()
            for row in range(5):
                name = f"block_{row}"
                y = 420 - row * 45
                self.engine.add_box(name, 380, y, 60, 40, mass=6.0, friction=0.8, color=(46, 204, 113))
                actions.append(f"Stacked {name}")
            return "Stacked a 5-tier vertical column. Demonstrates gravitational equilibrium and stability thresholds under horizontal disturbance.", actions

        else:
            # Default fallback: spawn a pair of interacting bodies
            self.engine.add_circle(f"ball_{len(self.engine.named_bodies)}", 380, 120, 22, mass=4.0, elasticity=0.85, color=(52, 152, 219))
            actions.append("Spawned dynamic sphere")
            return f"Simulation running (Offline mode). Tip: Configure your OpenAI API Key in Settings for full natural-language synthesis! Received: '{text}'", actions
