# Gemma Rover

TODO - add video of the rover in action

## Project Overview
Gemma Rover uses a Gemma 3n model to control a LeKiwi robot in a Mars-like environment. The project showcases Gemma 3n’s ability to make real-time decisions locally in a robotics context. This is crucial in scenarios where cloud services are not available and human support is 30 minutes away. This setup highlights the potential of running large language models on-device for autonomous, context-aware behavior in remote or constrained environments.

## Hardware Setup and Communication
The project uses a LeKiwi robot, a Macbook with an M2 chip and a travel router to connect the two devices. The Macbook is used to run the Gemma 3n model and the ACT models used for arm manipulation. Communication between the Macbook and the robot is done over a local network using ZeroMQ. 

In the future, we could use a Jetson AGX Orin(or maybe even a Jetson Orin Nano) to remove the need for a Macbook, but we didn't have one available at the time of the project.

## Control Loop
We were planning on using an agentic framework like ADK or smolagents for making decisions but we couldn't make them fit our use case and decided to implement our own setup that calls the LLM directly. Since this is a rover on Mars, it should think continuously, not just try to do a task and wait for further instructions. It should also be able to stop doing the task if there are threats to it's safety or it's longterm operational integrity.
The way we think about it is that the rover should get the information it needs (about the environment, about itself and it's homebase, about it's long running task) every few seconds and decide what to do next.

So we implemented what we call an Agentic Control Loop. On the main thread, we have a loop that prompts the LLM every few seconds with the current state of the robot and the environment. The LLM then decides what action to do next and spawns a thread to execute that action. In most cases, the action will take longer that it takes to go through the loop, so if the LLM decides to do the same action, nothing will happen. However, if it decides to do a different action, it will cancel the previous action and spawn a new thread to execute that action. This way, the LLM can make decisions in close to real-time. 

In our current setup, Gemma 3n:4eb is used on a Macbook(M2) and the loop runs at about 30 instructions per minute. For our tests, we capped this at 3 instructions per minute(run the loop every 20 seconds) to avoid having too many logs, but depending on the task, it can be increased.

Here is a log from a simulation run using "start_mars_simulation.py": https://gist.github.com/vladfatu/232492b4325303631e0f3a55dec81442
The scenario is the one from the video at the start, the rover has a long running task of collecting dirt samples. At some point, a dust storm starts and the rover needs to seek shelter. After the storm passes, it needs to clean the solar panel and then continue with the long running task.

#### Future Improvements
- the current implementation of the Agentic Control Loop was built specifically for this project, but it could be generalized to work in other scenarios where continuous monitoring and decision-making are required, like home automation, industrial automation, or other robotics applications.
- the current implementation only uses the name of functions to pass on to the Gemma 3n model, but this could be implemented the same way Agent frameworks do it, by passing on the function signature and the arguments. This would allow for more complex actions to be added.
- we could make Gemma 3n predict the next few actions instead of just the next one and let it know what it predicted the last time. This was not an issue in our scenario, but in a more complex environment, this could make the decision making more stable.
- the current prompt is very simple(zero shot), and will need to be expanded if we want to add more complex tasks. We were pleasantly surprised that pretty much the first prompt we tried worked for the entire scenario, and since it was short, elegant and did the job, we kept it. However, for a more complicated scenario, we would probably need to add more context, better define the priorities and provide examples of complicated decisions.

## Navigation
The rover uses the LeRobot framework for navigation. It can navigate to specific locations using QR codes placed in the environment. The navigation is done using the `move_robot_to_qr_code` function from the `navigation.py` file, which moves the robot in front of a specific QR code location.

#### Future Improvements
- navigation was not a big focus of this project and it currently is a bit jittery and slow. There are obvious improvements that can be made here, both in terms of code, but also in terms of hardware. The cameras used don't have good resolution or image stabilization, so the robot needs to move slowly to avoid losing the QR code.

## Arm Manipulation
The rover uses the LeRobot framework and more specifically the [ACT](https://tonyzhaozh.github.io/aloha/) policy for arm manipulation. This is a state-of-the-art imitation learning policy that can learn complex tasks from relatively few demonstrations. 
We have defined 7 actions that the rover can do. The datasets we recorded and the trained models for each action are open-sourced and are linked bellow, next to each action:

1 - **Pick up the scoop**: The rover can pick up the red scoop from a specific location next to the homebase. The dataset used to train this action is available [here](https://huggingface.co/spaces/lerobot/visualize_dataset?path=%2Fvladfatu%2Fgemma_rover_scoop_up_to_5%2Fepisode_0). The trained model is available [here](https://huggingface.co/vladfatu/gemma_rover_scoop_up_to_4).

2 - **Put the scoop back**: The rover can put the scoop back in the same location it picked it up from. The dataset used to train this action is available [here](https://huggingface.co/spaces/lerobot/visualize_dataset?path=%2Fvladfatu%2Fgemma_rover_scoop_drop_up_to_7%2Fepisode_0). The trained model is available [here](https://huggingface.co/vladfatu/gemma_rover_scoop_drop_up_to_7).

3 - **Pick up the towel**: The rover can pick up the towel from a specific location next to the homebase. The dataset used to train this action is available [here](https://huggingface.co/spaces/lerobot/visualize_dataset?path=%2Fvladfatu%2Fgemma_rover_cloth_up_to_5%2Fepisode_0). The trained model is available [here](https://huggingface.co/vladfatu/gemma_rover_cloth_up_to_5).

4 - **Put the towel back**: The rover can put the towel back in the same location it picked it up from. The dataset used to train this action is available [here](https://huggingface.co/spaces/lerobot/visualize_dataset?path=%2Fvladfatu%2Fgemma_rover_cloth_drop_up_to_3%2Fepisode_0). The trained model is available [here](https://huggingface.co/vladfatu/gemma_rover_cloth_drop_up_to_3).

5 - **Pick up dirt sample**: The rover can pick up a dirt sample from a specific location in the environment. The dataset used to train this action is available [here](https://huggingface.co/spaces/lerobot/visualize_dataset?path=%2Fvladfatu%2Fgemma_rover_dig_up_to_5%2Fepisode_0). The trained model is available [here](https://huggingface.co/vladfatu/gemma_rover_cloth_dig_up_to_5).

6 - **Put the dirt sample in the drop zone**: The rover can put the dirt sample in a specific drop zone. The dataset used to train this action is available [here](https://huggingface.co/spaces/lerobot/visualize_dataset?path=%2Fvladfatu%2Fgemma_rover_drop_dirt_up_to_5%2Fepisode_0). The trained model is available [here](https://huggingface.co/vladfatu/gemma_rover_drop_dirt_up_to_5).

7 - **Wipe the solar panel**: The rover can wipe the solar panel using the towel. The dataset used to train this action is available [here](https://huggingface.co/spaces/lerobot/visualize_dataset?path=%2Fvladfatu%2Fgemma_rover_wipe_solar_up_to_5%2Fepisode_0). The trained model is available [here](https://huggingface.co/vladfatu/gemma_rover_wipe_solar_up_to_5).

#### Future Improvements
 - more training examples in different conditions would help the models generalize better. The datasets were recorded in a garage and the lighting conditions were different than outside. The results were still pretty good but only in morning or evening light. During the day, they would strugle to do the task.
 - we used one model for each action, but we could have used a single more generic model that could do all the tasks. This would probably not work that well with ACT, but it should work with a VLA model like pi0, groot or smolVLA. the downside of this is that the model would be considerably larger and for our current setup, it might be hard to run both the Gemma 3n model and the VLA model on the same device. However, this is a good direction to explore for future improvements.

# Setup Instructions

#### Setup Prerequisites
The project was done using a Macbook(M2) and a LeKiwi robot(raspberry pi 5). You should be able to easily set it up with Linux or Windows with a few tweaks, but we've only tested the provided instructions for MacOS.

## Simulation Setup
This section helps you setup so you can run Gemma Rover in simulation on your laptop, no physical robot required. You will be able to see Gemma 3n make decisions in the defined scenario by choosing the next actions. Robot actions will be printed in the console.

Clone the gemma-rover repo and it's submodules
```bash
git clone --recurse-submodules https://github.com/vladfatu/gemma-rover.git
cd gemma-rover
```

Install poetry if you don't have it already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Install dependencies:
```bash
poetry install
```

Download and install Ollama from https://ollama.com/download

Download Gemma 3n:4eb
```bash
ollama run gemma3n:e4b
```

Run simulation
```bash
poetry run python start_mars_simulation.py
```


## Full Setup(with robot)
This section helps you setup a LeKiwi robot on top of the previous simulation setup. This is a lot more involved than the simulation step but it will allow you to run the actions on the robot.

#### Build your LeKiwi robot by following the instructions in the [LeKiwi repository](https://github.com/SIGRobotics-UIUC/LeKiwi)
Make sure to take note of your robot's ip address and the ports of your cameras

### Setup gemma-rover on the raspberry pi:

Clone our modified version of LeRobot:
```bash
git clone https://github.com/vladfatu/lerobot.git
cd lerobot
checkout feature/gemma_rover
```

Install dependencies:
```bash
poetry install
```

Start listening for commands:
```bash
poetry run python -m src.lerobot.robots.lekiwi.lekiwi_host --robot.id=gemma-rover
```

### On your laptop:

Change the robot's ip address in 'base/lerobot_task_handler.py' to match your robot's ip address:
```python
robot_config = LeKiwiClientConfig(remote_ip="your_robot_ip", id="gemma-rover")
```

Change the following line in 'start_mars_simulation.py' from:
```python
controller = GemmaThinkingLoop(state, use_real_robot=False)
```
to:
```python
controller = GemmaThinkingLoop(state, use_real_robot=True)
```

Start the simulation:
```bash
poetry run python start_mars_simulation.py
```

## !!! Warning
The LeRobot models used were trained on our datasets that used our robot with our environment. When you use a different robot, the calibration of the motors will be a bit different. You can try to run the models as they are, but make sure to have a fast way to disconnecting it if it starts moving strangely. You will most likely need to record your own datasets and train the models for the LeRobot actions. Feel free to define your own actions as changing the code to support new actions should be pretty straightforward. For help with training new models, check out the [LeRobot documentation](https://huggingface.co/docs/lerobot/main/en/il_robots#train-a-policy)


## Citation

This project was created for submission to the [Google - The Gemma 3n Impact Challenge](https://kaggle.com/competitions/google-gemma-3n-hackathon):

```bibtex
@misc{google-gemma-3n-hackathon,
    author = {Glenn Cameron and Omar Sanseviero and Gus Martins and Ian Ballantyne and Kat Black and Mark Sherwood and Milen Ferev and Ronghui Zhu and Nilay Chauhan and Pulkit Bhuwalka and Emily Kosa and Addison Howard},
    title = {Google - The Gemma 3n Impact Challenge},
    year = {2025},
    howpublished = {\url{https://kaggle.com/competitions/google-gemma-3n-hackathon}},
    note = {Kaggle}
}
```

It makes use of the [LeRobot](https://github.com/huggingface/lerobot) framework, which is a state-of-the-art machine learning framework for robotics in Pytorch:

```bibtex
@misc{cadene2024lerobot,
    author = {Cadene, Remi and Alibert, Simon and Soare, Alexander and Gallouedec, Quentin and Zouitine, Adil and Palma, Steven and Kooijmans, Pepijn and Aractingi, Michel and Shukor, Mustafa and Aubakirova, Dana and Russi, Martino and Capuano, Francesco and Pascale, Caroline and Choghari, Jade and Moss, Jess and Wolf, Thomas},
    title = {LeRobot: State-of-the-art Machine Learning for Real-World Robotics in Pytorch},
    howpublished = "\url{https://github.com/huggingface/lerobot}",
    year = {2024}
}
```

It uses the [ACT](https://tonyzhaozh.github.io/aloha/) policy for complex arm manipulation tasks:

```bibtex
@article{zhao2023learning,
  title={Learning fine-grained bimanual manipulation with low-cost hardware},
  author={Zhao, Tony Z and Kumar, Vikash and Levine, Sergey and Finn, Chelsea},
  journal={arXiv preprint arXiv:2304.13705},
  year={2023}
}
```

The physical rover is based on the [LeKiwi](https://github.com/SIGRobotics-UIUC/LeKiwi) robot, which is a low-cost, open-source robot platform:

```bibtex
@misc{sigrobotics2024lekiwi,
    author = {SIGRobotics},
    title = {LeKiwi: Low-Cost Mobile Manipulator},
    howpublished = "\url{https://github.com/SIGRobotics-UIUC/LeKiwi}",
    year = {2025}
}
```

