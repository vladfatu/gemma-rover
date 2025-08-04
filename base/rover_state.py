from enum import Enum
import threading
import json

class RoverState:
    def __init__(self):
        self._lock = threading.Lock()

        self.inside_base = True
        self.is_holding_scoop = False
        self.is_holding_towel = False
        self.has_dirt_sample = False
        self.solar_panel_dirty = False
        self.storm_watch_status = RoverStormWatchStatus.NO_STORM
        self.long_running_task = "Gather dirt samples and move them to the drop zone"
  
    def update_state(self, **kwargs):
        with self._lock:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def get_snapshot(self):
        with self._lock:
            return {
                "inside_base": self.inside_base,
                "is_holding_scoop": self.is_holding_scoop,
                "is_holding_towel": self.is_holding_towel,
                "has_dirt_sample": self.has_dirt_sample,
                "solar_panel_dirty": self.solar_panel_dirty,
                "storm_watch_status": self.storm_watch_status,
                "long_running_task": self.long_running_task
            }

    def to_prompt_string(self):
        with self._lock:
            return json.dumps({
                "inside_base": self.inside_base,
                "is_holding_scoop": self.is_holding_scoop,
                "is_holding_towel": self.is_holding_towel,
                "has_dirt_sample": self.has_dirt_sample,
                "solar_panel_dirty": self.solar_panel_dirty,
                "storm_watch_status": self.storm_watch_status.value,
                "long_running_task": self.long_running_task
            }, indent=2)

class RoverStormWatchStatus(Enum):
    INCOMING_STORM = "Incoming Storm"
    STORM_ONGOING = "Storm Ongoing"
    NO_STORM = "No Storm"

