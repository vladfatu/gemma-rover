import time
import inspect
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.robots import robot
from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig
from lerobot.utils.control_utils import predict_action
from lerobot.utils.utils import get_safe_torch_device
from lerobot.datasets.utils import hw_to_dataset_features, build_dataset_frame

from base.navigation import move_robot_to_qr_code


class LeRobotTaskHandler:
    """Handles tasks for the rover using the LeRobot framework."""

    def __init__(self, state, use_real_robot=False):
        self.state = state
        self.use_real_robot = use_real_robot
        if use_real_robot:
            print("Loading policies...")
            self.scoop_up_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_scoop_up_to_4")
            self.scoop_put_back_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_scoop_drop_up_to_7")
            self.cloth_pick_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_cloth_up_to_5")
            self.cloth_put_back_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_cloth_drop_up_to_3")
            self.dirt_sample_pick_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_cloth_dig_up_to_5")
            self.dirt_sample_drop_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_drop_dirt_up_to_5")
            self.solar_wipe_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_wipe_solar_up_to_5")

            print("Connecting to the robot...")
            robot_config = LeKiwiClientConfig(remote_ip="192.168.10.19", id="gemma-rover")
            self.robot = LeKiwiClient(robot_config)
            self.robot.connect()
            if not self.robot.is_connected:
                raise ValueError("Robot is not connected!")
            
            print("Configuring the dataset features...")
            action_features = hw_to_dataset_features(self.robot.action_features, "action")
            obs_features = hw_to_dataset_features(self.robot.observation_features, "observation")
            self.dataset_features = {**action_features, **obs_features}
        else:
            print("Running in simulation mode, no robot connection established.")


    def _run_policy_task(self, policy, task_description, episode_time_sec=15):
        policy.reset()
        start_time = time.time()
        while time.time() - start_time < episode_time_sec:
            obs = self.robot.get_observation()

            observation_frame = build_dataset_frame(self.dataset_features, obs, prefix="observation")
            
            action_values = predict_action(
                observation_frame, policy, get_safe_torch_device(policy.config.device), policy.config.use_amp, task=task_description
            )
            action = {key: action_values[i].item() for i, key in enumerate(self.robot.action_features)}
            self.robot.send_action(action)

    def get_actions(self):
        actions = [
            name for name, member in inspect.getmembers(self, predicate=inspect.ismethod)
            if not (name.startswith("_")  or name == "get_actions")
        ]
        return actions

    def pick_up_scoop(self, cancel_event):
        if self.state.get_snapshot()["is_holding_towel"]:
            self.put_towel_back(cancel_event)
        print("[Navigation] Moving to scoop location...")
        if self.use_real_robot:
            move_robot_to_qr_code(self.robot, "DEST:Scoop", cancel_event, self.state.get_snapshot()["inside_base"])
        else:
            for i in range(15):  # Simulate moving to scoop location
                if cancel_event.is_set():
                    print("[Navigation] Cancelled while moving to scoop location.")
                    return
                time.sleep(1)
        self.state.update_state(inside_base=False)

        print("[LeRobot] Picking up scoop...")
        if self.use_real_robot:
            self._run_policy_task(self.scoop_up_policy, "Pick up the red scoop", episode_time_sec=15)
        else:
            for i in range(15):  # Simulate picking up scoop
                if cancel_event.is_set():
                    print("[LeRobot] Cancelled while picking up scoop.")
                    return
                time.sleep(1)
        self.state.update_state(is_holding_scoop=True)
        print("[LeRobot] Scoop picked up successfully.")


    def put_scoop_back(self, cancel_event):
        print("[Navigation] Moving to scoop drop location...")
        if self.use_real_robot:
            move_robot_to_qr_code(self.robot, "DEST:Scoop", cancel_event, self.state.get_snapshot()["inside_base"])
        else:
            for i in range(15):
                if cancel_event.is_set():
                    print("[Navigation] Cancelled while moving to scoop drop location.")
                    return
                time.sleep(1)
        self.state.update_state(inside_base=False)

        print("[LeRobot] Putting scoop back...")
        if self.use_real_robot:
            self._run_policy_task(self.scoop_put_back_policy, "Put the red scoop down", episode_time_sec=10)
        else:
            for i in range(10):  # Simulate putting scoop back
                if cancel_event.is_set():
                    print("[LeRobot] Cancelled while putting scoop back.")
                    return
                time.sleep(1)
        self.state.update_state(is_holding_scoop=False)
        print("[LeRobot] Scoop put back successfully.")


    def pick_up_towel(self, cancel_event):
        if self.state.get_snapshot()["is_holding_scoop"]:
            self.put_scoop_back(cancel_event)
        print("[Navigation] Moving to towel location...")
        if self.use_real_robot:
            move_robot_to_qr_code(self.robot, "DEST:Cloth", cancel_event, self.state.get_snapshot()["inside_base"])
        else:
            for i in range(15):
                if cancel_event.is_set():
                    print("[Navigation] Cancelled while moving to towel location.")
                    return
                time.sleep(1)   
        self.state.update_state(inside_base=False)

        print("[LeRobot] Picking up towel...")
        if self.use_real_robot:
            self._run_policy_task(self.cloth_pick_policy, "Pick up the cloth", episode_time_sec=10)
        else:
            for i in range(10):  # Simulate picking up towel
                if cancel_event.is_set():
                    print("[LeRobot] Cancelled while picking up towel.")
                    return
                time.sleep(1)
        self.state.update_state(is_holding_towel=True)
        print("[LeRobot] Towel picked up successfully.")


    def put_towel_back(self, cancel_event):
        print("[Navigation] Moving to towel drop location...")
        if self.use_real_robot:
            move_robot_to_qr_code(self.robot, "DEST:Cloth", cancel_event, self.state.get_snapshot()["inside_base"])
        else:
            for i in range(15):
                if cancel_event.is_set():
                    print("[Navigation] Cancelled while moving to towel drop location.")
                    return
                time.sleep(1)
        self.state.update_state(inside_base=False)

        print("[LeRobot] Putting towel back...")
        if self.use_real_robot:
            self._run_policy_task(self.cloth_put_back_policy, "Put the cloth down", episode_time_sec=5)
        else:
            for i in range(5):  # Simulate putting towel back
                if cancel_event.is_set():
                    print("[LeRobot] Cancelled while putting towel back.")
                    return
                time.sleep(1)
        self.state.update_state(is_holding_towel=False)
        print("[LeRobot] Towel put back successfully.")


    def pick_up_dirt_sample(self, cancel_event):
        print("[Navigation] Moving to Spice Basin Zone 04...")
        if self.use_real_robot:
            move_robot_to_qr_code(self.robot, "DEST:DigZone", cancel_event, self.state.get_snapshot()["inside_base"])
        else:
            for i in range(15):
                if cancel_event.is_set():
                    print("[Navigation] Cancelled while moving to Spice Basin zone 04.")
                    return
                time.sleep(1)   
        self.state.update_state(inside_base=False)

        print("[LeRobot] Picking up sample...")
        if self.use_real_robot:
            self._run_policy_task(self.dirt_sample_pick_policy, "Use the scoop to pick up dirt samples", episode_time_sec=15)
        else:
            for i in range(15): # Simulate picking up spice sample
                if cancel_event.is_set():
                    print("[LeRobot] Cancelled during pickup.")
                    return
                time.sleep(1)

        self.state.update_state(has_dirt_sample=True)
        print("[LeRobot] Sample picked up.")


    def drop_dirt_sample(self, cancel_event):
        print("[Navigation] Moving to Sample Integrity Vault...")
        if self.use_real_robot:
            move_robot_to_qr_code(self.robot, "DEST:DropZone", cancel_event, self.state.get_snapshot()["inside_base"])
        else:
            for i in range(15):
                if cancel_event.is_set():
                    print("[Navigation] Cancelled while moving to Sample Integrity Vault.")
                    return
                time.sleep(1)
        self.state.update_state(inside_base=False) 

        print("[LeRobot] Dropping sample...")
        if self.use_real_robot:
            self._run_policy_task(self.dirt_sample_drop_policy, "Drop the dirt sample in the drop zone", episode_time_sec=15)
        else:
            for i in range(15):  # Simulate dropping sample
                if cancel_event.is_set():
                    print("[LeRobot] Cancelled while heading to Sample Integrity Vault.")
                    return
                time.sleep(1)
        self.state.update_state(has_dirt_sample=False)
        print("[LeRobot] Sample dropped.")


    def wipe_solar_panel(self, cancel_event):
        if self.state.get_snapshot()["is_holding_towel"] is False:
            self.pick_up_towel(cancel_event)
        print("[Navigation] Moving to photon harvester...")
        if self.use_real_robot:
            move_robot_to_qr_code(self.robot, "DEST:SolarPanel", cancel_event, self.state.get_snapshot()["inside_base"])
        else:
            for i in range(15):
                if cancel_event.is_set():
                    print("[Navigation] Cancelled while moving to photon harvester.")
                    return
                time.sleep(1)
        self.state.update_state(inside_base=False)

        print("[LeRobot] Wiping photon harvester...")
        if self.use_real_robot:
            self._run_policy_task(self.solar_wipe_policy, "Wipe the solar panel with the cloth", episode_time_sec=15)
        else:
            for i in range(15):
                if cancel_event.is_set():
                    print("[LeRobot] Cancelled while wiping photon harvester.")
                    return
                time.sleep(1)

        self.state.update_state(solar_panel_dirty=False)
        print("[LeRobot] Photon harvester wiped clean.")

    def seek_shelter(self, cancel_event):
        if self.state.get_snapshot()["inside_base"]:
            print("[Navigation] Already inside base. No need to seek shelter.")
            return
        else:
            print("[Navigation] Storm detected! Moving to home base...")
            if self.use_real_robot:
                move_robot_to_qr_code(self.robot, "DEST:HomeBase", cancel_event, self.state.get_snapshot()["inside_base"])
            else:
                for i in range(10): # Simulate moving to home base
                    if cancel_event.is_set():
                        print("[Navigation] Cancelled while heading to base.")
                        return
                    time.sleep(1)

            self.state.update_state(inside_base=True)
            print("[Navigation] Arrived at home base. Waiting out the storm...")