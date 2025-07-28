from enum import Enum

class RoverState:
    def __init__(self):
        self.inside_base = True
        self.has_scoop = False
        self.has_cloth = False
        self.has_dirt_sample = False
        self.storm_watch_status = RoverStormWatchStatus.NO_STORM
        self.long_running_task = "Gather dirt samples and move them to drop zone"

    def to_prompt_string(self):
        return f"""
        Current State:
        - Inside base: {self.inside_base}
        - Has scoop: {self.has_scoop}
        - Has cloth: {self.has_cloth}
        - Has dirt sample: {self.has_dirt_sample}
        - Storm status: {self.storm_watch_status.value}
        - Long running task: {self.long_running_task}
        """

class RoverStormWatchStatus(Enum):
    INCOMING_STORM = "Incoming Storm"
    STORM_ONGOING = "Storm Ongoing"
    NO_STORM = "No Storm"

