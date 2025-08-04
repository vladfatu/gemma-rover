
import threading
import time
from base.control_loop import GemmaThinkingLoop
from base.rover_state import RoverState, RoverStormWatchStatus
from base.lerobot_task_handler import LeRobotTaskHandler


state = RoverState()
controller = GemmaThinkingLoop(state, use_real_robot=False)
controller.start()

# Optional: simulate storm after some time

def trigger_storm_warning():
    time.sleep(120)
    print("[Mars Environment] Simulating incoming storm...")
    state.update_state(storm_watch_status=RoverStormWatchStatus.INCOMING_STORM)

threading.Thread(target=trigger_storm_warning).start()


def trigger_storm():
    time.sleep(170)
    print("[Mars Environment] Simulating storm...")
    state.update_state(storm_watch_status=RoverStormWatchStatus.STORM_ONGOING)

threading.Thread(target=trigger_storm).start()


def trigger_storm_end():
    time.sleep(220)
    print("[Mars Environment] Simulating storm end...")
    state.update_state(storm_watch_status=RoverStormWatchStatus.NO_STORM)
    state.update_state(solar_panel_dirty=True)

threading.Thread(target=trigger_storm_end).start()

# Let it run for a while
time.sleep(2000000)
controller.stop()
