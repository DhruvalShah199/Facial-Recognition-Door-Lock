# Facial-Recognition-Door-Lock
This project code is for a Facial Recognition Door Lock with Keypad PIN Input on Raspberry Pi
## Functional features
This Facial recognition security device will check whether a person is registered to enter or not along with a passcode entry system if the face is not detected. The face is detected via a camera, which is connected to Raspberry Pi. If the person’s face is detected, the buzzer will buzz once with a green LED and the servomotor won't move (0 degrees). The program tries to detect a face for 20 seconds. If not, it will display a message on an LCD screen and the user will be asked to enter the passcode, all connected to Raspberry Pi. If entered correctly the servomotor will move up (180 degrees) and if not, the buzzer will buzz with a red LED and the servomotor stays at the rest position (0 degrees).
## Components required
- Raspberry Pi 3B+
- 4x4 Matrix array Keypad
- Servomotor (SG90)
- Pi Camera Module
- 1602A LCD Screen
- Buzzer
- LEDs and wires
- T-cobbler for Raspberry Pi
## Connections
- The Pi Camera is directly connected to camera module pin on Raspberry Pi.
- The input end of the Keypad (first four pins from the left) are connect to GPIO pins 5,6,13 and 19 respectively. The remaining fours pins (output pins) are connected to GPIO pins 12,16,20 and 21 respectively.
- The servomotor is connected to the GND pin and GPIO pin 25.
- The LCD screen is connected on pins SDA1, SCL1, 5V and GND.
- The LEDs are connected on pins GPIO 26 (green) and GPIO 27 (red) and the buzzer is connected on pins GPIO 23 and GND.


![Schematics](https://user-images.githubusercontent.com/73520531/195213791-49ac2313-d4c7-42a8-bb8c-44df3a115032.jpg)

## Code Explaination
- Run the [facial_dataset.py](https://github.com/DhruvalShah199/Facial-Recognition-Door-Lock/blob/main/Codes/facial_dataset.py) code first. This code will take 50 photos of a user and will save it in a folder "dataset". Make sure to input different user id for different users.
- Run the [facial_recognition_training.py](https://github.com/DhruvalShah199/Facial-Recognition-Door-Lock/blob/main/Codes/facial_recognition_training.py) code after that. This code recognises the frontal face from the 50 photos captured and trains the code to recognise it as the specified user by following "haarcascade_frontalface_default.xml".
- In the end, run the [main.py](https://github.com/DhruvalShah199/Facial-Recognition-Door-Lock/blob/main/Codes/main.py) code for the final setup.
