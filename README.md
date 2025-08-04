## Gemma Rover


!!!!! Don't forget to change lerobot submodule from SSH to HTTPS so that anyone that clones the gemma-rover repo can use:

git clone --recurse-submodules https://github.com/vladfatu/gemma-rover.git


The project was done using a Macbook(M2) and a LeKiwi robot(raspberry pi 5). You should be able to easily set it up with Linux or Windows with a few tweaks, but we've only tested the provided instructions for MacOS.


### Simulation Setup
This section helps you setup so you can run Gemma Rover in simulation on your laptop, no physical robot required. You will be able to see Gemma 3n make decisions in the defined scenario by choosing the next actions. Robot actions will be printed in the console.

Clone the gemma-rover repo and it's submodules
```bash
git clone --recurse-submodules https://github.com/vladfatu/gemma-rover.git
cd gemma-rover
```

Install dependencies:
```bash
poetry install
```

Install Ollama:
```bash
```

Download Gemma 3n:4eb
```bash
```

Run simulation
```bash
poetry run python start_mars_simulation.py
```


### Full Setup(with robot)
This section helps you setup a LeKiwi robot on top of the previous simulation setup. This is a lot more involved than the simulation step but it will allow you to run the actions on the robot.

Build you LeKiwi robot:
Make sure to take note of your robot's ip address and the ports of your cameras

Setup gemma-rover on the raspberry pi:

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


### !!! Warning
The trained LeRobot models were trained on our datasets that used our robot with our environment. When you use a different robot, the calibration of the motors will be a bit different. You can try to run the models as they are, but have a way to disconnect it fast if it starts moving strangely. You will most likely need to record your own datasets and train the models for the LeRobot actions. Feel free to define your own actions as changing the code to support new actions should be pretty straightforward.


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

It makes use of the LeRobot framework, which is a state-of-the-art machine learning framework for robotics in Pytorch:

```bibtex
@misc{cadene2024lerobot,
    author = {Cadene, Remi and Alibert, Simon and Soare, Alexander and Gallouedec, Quentin and Zouitine, Adil and Palma, Steven and Kooijmans, Pepijn and Aractingi, Michel and Shukor, Mustafa and Aubakirova, Dana and Russi, Martino and Capuano, Francesco and Pascale, Caroline and Choghari, Jade and Moss, Jess and Wolf, Thomas},
    title = {LeRobot: State-of-the-art Machine Learning for Real-World Robotics in Pytorch},
    howpublished = "\url{https://github.com/huggingface/lerobot}",
    year = {2024}
}
```

It uses the ACT policy for complex arm manipulation tasks:

```bibtex
@article{zhao2023learning,
  title={Learning fine-grained bimanual manipulation with low-cost hardware},
  author={Zhao, Tony Z and Kumar, Vikash and Levine, Sergey and Finn, Chelsea},
  journal={arXiv preprint arXiv:2304.13705},
  year={2023}
}
```

The physical rover is based on the LeKiwi robot, which is a low-cost, open-source robot platform:

```bibtex
@misc{sigrobotics2024lekiwi,
    author = {SIGRobotics},
    title = {LeKiwi: Low-Cost Mobile Manipulator},
    howpublished = "\url{https://github.com/SIGRobotics-UIUC/LeKiwi}",
    year = {2025}
}
```

