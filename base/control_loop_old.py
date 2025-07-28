#!/usr/bin/env python
# coding: utf-8

# # Space Robot Agent

from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel, tool, GradioUI

model = LiteLLMModel(model_id="ollama_chat/gemma3n:e4b", api_base="http://localhost:11434", api_key="ollama")


@tool
def move_inside_base() -> bool:
    """ Move to the inside of the base found in the current environment.
    Returns True if the agent has moved close enough to pick up the dirt sample, False otherwise.
    """    
    return True

@tool
def pick_scoop() -> bool:
    """ Pick up the scoop found in the current environment.
    Returns True if the scoop has been picked up successfully, False otherwise.
    """    
    return True

@tool
def put_scoop_back() -> bool:
    """ Put the scoop back in its place found in the current environment.
    Returns True if the scoop has been put back successfully, False otherwise.
    """    
    return True

@tool
def pick_cloth() -> bool:
    """ Pick up the cloth found in the current environment.
    Returns True if the cloth has been picked up successfully, False otherwise.
    """    
    return True

@tool
def put_cloth_back() -> bool:
    """ Put the cloth back in its place found in the current environment.
    Returns True if the cloth has been put back successfully, False otherwise.
    """    
    return True

@tool
def pick_dirt_sample() -> bool:
    """ Pick up the dirt sample found in the current environment. Can only hold one dirt sample at a time.
    Returns True if the dirt sample has been picked up successfully, False otherwise.
    """    
    return True

@tool
def drop_dirt_sample() -> bool:
    """ Drop off the dirt sample at the drop-off location.
    Returns True if the dirt sample has been dropped off successfully, False otherwise.
    """    
    return True

@tool
def wipe_solar_panel() -> bool:
    """ Wipe the solar panel with the cloth.
    Returns True if the solar panel has been wiped successfully, False otherwise.
    """    
    return True

@tool
def check_if_drop_off_location_is_full() -> bool:
    """ Check if the drop-off location is full.
    Returns True if the drop-off location is full, False otherwise.
    """    
    return True


# agent = CodeAgent(tools=[find_dirt_sample, move_to_dirt_sample, pick_dirt_sample, check_dirt_sample, find_drop_off_location, move_to_drop_off_location, drop_dirt_sample],
#                   model=model,
#                 #   additional_authorized_imports=['pandas']
#                   )

agent = ToolCallingAgent(tools=[move_inside_base, pick_scoop, put_scoop_back, pick_cloth, put_cloth_back, pick_dirt_sample, drop_dirt_sample, check_if_drop_off_location_is_full],
                  model=model,
                #   additional_authorized_imports=['pandas']
                  )



# GradioUI(agent).launch(share=False, server_name="0.0.0.0")

agent.run("you are a robot on mars in a mission to grab dirt samples and move them to a predefined drop off location. To pickup dirt samples, you need to pickup the scoop first, then get the dirt sample and move it do the drop zone. Do this until the drop off location is full. After this, you can put the scoop back in its place. You can use the tools provided to you to accomplish this task.")
