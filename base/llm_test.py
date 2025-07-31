import json
from rover_state import RoverState
import ollama


snapshot = RoverState().get_snapshot()

# Format the state into a system prompt or context
prompt = f"""
You are a control agent for a Mars rover. Based on the current state of the rover, decide what action it should take next. 
Respond only with one of the following function names (as plain text): 
- pickup_dirt_sample
- seek_shelter
- wait

State:
{json.dumps(snapshot, indent=2)}
"""

try:
    response = ollama.chat(
        model="gemma3n:e4b",  # Or another local model you have
        messages=[
            {"role": "system", "content": "You are a Mars rover control agent."},
            {"role": "user", "content": prompt}
        ]
    )
except Exception as e:
    print(f"Error communicating with LLM: {e}")
    response = {"message": {"content": "wait"}}

model_reply = response["message"]["content"].strip().lower()
print(f"[LLM] Suggested action: {model_reply}")