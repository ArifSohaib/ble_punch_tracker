# BLE Punch Tracker

## Components:
### Arduino side; 
- On the arduino side we have a .ino file written in C++ 
- This starts a BLE server and uses the built in Accelerometer in the IMU of Arduino Nano 33 BLE Sense. 
- The same can be changed to use something like an ESP32 with an external IMU like BNO055 

### Web component:
- This is a  website that connects to the Arduino server and reads the data 
- As it reads the data it sends it to a local SQLite file that can be queried
- This file is used to plot a grapah showing the readings from the accelerometer
- It is important that this component work in tandum with the Arduinoi component in real time otherwise the application does not work. 


### LLM text feedback component:
- This component reads from the sql server and offer insights about the workout sessions
- This will also be running locally on an AMD GPU to save costs
- It does not need to be  real time since it offers advice after the fact
- It does need good integration and grounding within the data 
- Optionally it may need rag input from known excerise sciencne books to ground the output in known facts as opposed to all the random training data it saw on the internet

### LLM voice component:
- Additionl component that will also use the local GPU to run a local model generating sound
- This will generate sound in both real time and after the fact to give insights about the workout 
- For some simple feedback, we can combine it with the Arduino and a speaker to have the punching bag respond



## Installation:

### Arduino
1. Open the Arduino IDE and install the board support package for **Arduino Nano 33 BLE Sense**.
2. Install the library for the built-in IMU (e.g., **Arduino_LSM9DS1**).
3. Upload the provided `.ino` code to the Arduino.
4. Test BLE output using **nRFConnect**:
   - The device will appear as `NANO33BLE_JSON`.
   - Open the **Unknown Service** and then the **Unknown Characteristic**.
   - Readings appear in JSON format (may be fragmented due to BLE packet limits).


### Web component:
Open a terminal and create a virtual environment using conda or your prefered environment maager 
If using Anaconda use the environment.yml to create the environment as:

```bash
conda env create -f environment.yml
```
Once the environment is created one time, you don't need to create it again.

Activate the environment, you need to do this every time before running the app. 
If using conda activate it using:
```bash
conda activate fastapi-workout
```

In the same terminal where you have the environment activated, run the application locally using:

```bash
python -m fastapi run main.py
```

If the application is running correctly you will see some logs and within the logs you will see:
```bash
server started at http://0.0.0.0:8000

```
Open your web browser and go to the page **http:\\localhost:8000** to use the application


## Usage

You will see two buttons;
`Start Workout` and `Stop Workout`

Before clicking start workout make sure that the Arduino is connected to some power source and is safely placed under the punching bag. Therre should be a zipper you can open underneath and place the arduino there. 

Once you have ensured that the Arduino is powered on then click Start Workout.
It will automatically detect the Arduino's BLE signiture and cocnnect and start the readings. 

You will see an "active" workout which is the one being tracked.

Before doing a full workout test everything out by punching the bag for a minute or so, then stopping the workout and clicking the  session start time

This will show you a graph representaing the directions and accelerations the bag experienced. 

# TO DO:
Update the LLM components