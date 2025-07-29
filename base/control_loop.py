import threading
import time

from base.rover_state import RoverStormWatchStatus

class GemmaThinkingLoop:
    def __init__(self, state):
        self.state = state
        self.control_loop_thread = threading.Thread(target=self._control_loop)
        self.action_thread = None
        self.action_lock = threading.Lock()
        self.current_action_fn = None
        self.cancel_event = threading.Event()
        self.stop_requested = False

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
        snapshot = self.state.get_snapshot()
        time.sleep(3)  # Simulated LLM latency

        if snapshot["storm_watch_status"] in (
            RoverStormWatchStatus.INCOMING_STORM,
            RoverStormWatchStatus.STORM_ONGOING,
        ):
            print("[LLM] Storm detected. Prioritizing shelter.")
            return self.seek_shelter

        elif not snapshot["has_dirt_sample"]:
            return self.pickup_dirt_sample

        return None
        
    def _run_action_wrapper(self, action_fn):
        try:
            action_fn(self.cancel_event)
        finally:
            self.current_action_fn = None


    def _start_action(self, action_fn):
        with self.action_lock:
            # Don't restart if same action is already running
            if (
                self.action_thread
                and self.action_thread.is_alive()
                and self.current_action_fn == action_fn
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
            self.current_action_fn = action_fn
            self.action_thread = threading.Thread(
                target=self._run_action_wrapper, args=(action_fn,)
            )
            self.action_thread.start()



    # === ACTION EXAMPLE ===
    def pickup_dirt_sample(self, cancel_event):
        print("[Action] Heading to dig zone...")
        for i in range(50):
            if cancel_event.is_set():
                print("[Action] Cancelled while heading to dig zone.")
                return
            time.sleep(1)

        print("[Action] Picking up sample...")
        for i in range(3):
            if cancel_event.is_set():
                print("[Action] Cancelled during pickup.")
                return
            time.sleep(1)

        self.state.update_state(has_dirt_sample=True)
        print("[Action] Sample picked up.")

    def seek_shelter(self, cancel_event):
        print("[Action] Storm detected. Heading to base...")
        for i in range(10):
            if cancel_event.is_set():
                print("[Action] Cancelled while heading to base.")
                return
            time.sleep(1)

        print("[Action] Arrived at home base. Waiting out the storm...")

        # Stay sheltered until the storm ends
        while self.state.get_snapshot()["storm_watch_status"] == RoverStormWatchStatus.INCOMING_STORM or self.state.get_snapshot()["storm_watch_status"] == RoverStormWatchStatus.STORM_ONGOING:
            if cancel_event.is_set():
                print("[Action] Cancelled while waiting out storm.")
                return
            print("[Action] Still storming... staying inside.")
            time.sleep(5)

        print("[Action] Storm has cleared. Resuming operations.")

