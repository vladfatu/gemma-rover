

from lerobot_task_handler import LeRobotTaskHandler
from rover_state import RoverState


state = RoverState()
gemma_rover = LeRobotTaskHandler(state)
gemma_rover.drop_dirt_sample(None)
# gemma_rover.pick_dirt_sample(None)
# gemma_rover.pick_scoop(None)
# gemma_rover.put_scoop_back(None)
# gemma_rover.pick_cloth(None)
# gemma_rover.put_cloth_back(None)
# gemma_rover.wipe_solar_panel(None)