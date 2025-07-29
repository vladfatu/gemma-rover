
import threading
import time
from base.control_loop import GemmaThinkingLoop
from base.rover_state import RoverState, RoverStormWatchStatus


state = RoverState()
controller = GemmaThinkingLoop(state)
controller.start()

# Optional: simulate storm after some time

def trigger_storm():
    time.sleep(10)
    state.update_state(storm_watch_status=RoverStormWatchStatus.INCOMING_STORM)

threading.Thread(target=trigger_storm).start()

# Let it run for a while
time.sleep(100)
controller.stop()
