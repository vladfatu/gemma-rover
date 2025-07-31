import threading
import time
import ollama

from base.lerobot_task_handler import LeRobotTaskHandler

class GemmaThinkingLoop:
    def __init__(self, state):
        self.state = state
        self.control_loop_thread = threading.Thread(target=self._control_loop)
        self.action_thread = None
        self.action_lock = threading.Lock()
        self.current_action_fn = None
        self.cancel_event = threading.Event()
        self.stop_requested = False
        self.gemma_rover = LeRobotTaskHandler(state)
        print("self.gemma_rover.get_actions():", self.gemma_rover.get_actions())

    def start(self):
        self.control_loop_thread.start()

    def stop(self):
        self.stop_requested = True
        self.cancel_event.set()
        self.control_loop_thread.join()
        if self.action_thread and self.action_thread.is_alive():
            self.action_thread.join()

    def _control_loop(self):
        while not self.stop_requested:
            start_time = time.time()

            print("[Control Loop] Thinking with LLM...")
            action_to_run = self._decide_next_action_with_llm()

            if self.stop_requested:
                break

            if action_to_run:
                self._start_action(action_to_run)

            elapsed = time.time() - start_time
            sleep_time = max(30.0 - elapsed, 0.0)
            print(f"[Control Loop] Sleeping {sleep_time:.1f}s before next cycle.")
            time.sleep(sleep_time)


    def _decide_next_action_with_llm(self):
        state = self.state.to_prompt_string()

        # Format the state into a system prompt or context
        prompt = f"""
    You are a control agent for a Mars rover. Based on the current state of the rover, decide what action it should take next.
    Your mission is to complete the long running task from the current state, but should prioritize safety and operational efficiency.
    Respond only with one of the following function names (as plain text):
    {self.gemma_rover.get_actions()}

    Current State:
    {state}
    """
        
        print(f"[LLM] Sending prompt to model: {prompt}")
        try:
            response = ollama.chat(
                model="gemma3n:e4b", 
                messages=[
                    {"role": "system", "content": "You are a Mars rover control agent."},
                    {"role": "user", "content": prompt}
                ]
            )

            model_reply = response["message"]["content"].strip().lower()
            print(f"[LLM] Suggested action: {model_reply}")

            return model_reply

        except Exception as e:
            print(f"[LLM ERROR] Failed to call Ollama: {e}")
            return None


        
    def _run_action_wrapper(self, action_fn_name):
        try:
            action_fn = getattr(self.gemma_rover, action_fn_name)
            action_fn(self.cancel_event)
        finally:
            self.current_action_fn = None


    def _start_action(self, action_fn_name):
        with self.action_lock:
            # Don't restart if same action is already running
            if (
                self.action_thread
                and self.action_thread.is_alive()
                and self.current_action_fn == action_fn_name
            ):
                print("[Action] Same action already running. Skipping restart.")
                return

            # Cancel current action if different
            if self.action_thread and self.action_thread.is_alive():
                print("[Action] Cancelling current action...")
                self.cancel_event.set()
                self.action_thread.join()
                print("[Action] Previous action stopped.")

            self.cancel_event.clear()
            self.current_action_fn = action_fn_name
            self.action_thread = threading.Thread(
                target=self._run_action_wrapper, args=(action_fn_name,)
            )
            self.action_thread.start()


