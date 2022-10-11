import cv2
import numpy as np
import os 
import RPi.GPIO as GPIO
import time
from gpiozero import Servo, Buzzer, LED
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD


# Set timer for face detection
timeout = time.time() + 60*0.33

lcd = LCD()

redLED = LED(27)
greenLED = LED(26)

buzzer = Buzzer(23)

# Servo pin output at GPIO25
servo = Servo(25)

servo.mid()

cnt = 0

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);

font = cv2.FONT_HERSHEY_SIMPLEX

#iniciate id counter
id = 0

# Setting names with their respective User ID
#          0        1           2       3    4
names = ['None', 'Dhruval', 'Sahithi', 'Z', 'W'] 

# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height

# Define minimum window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

lcd.clear()
lcd.text("Bring your face",1)
lcd.text("near the camera",2)

# These are the GPIO pin numbers where the
# lines of the keypad matrix are connected
L1 = 5
L2 = 6
L3 = 13
L4 = 19

# These are the four columns
C1 = 12
C2 = 16
C3 = 20
C4 = 21

# The GPIO pin of the column of the key that is currently
# being held down or -1 if no key is pressed
keypadPressed = -1

# Initializing passcode for entry
secretCode = "1999"
input = ""

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)

# Use the internal pull-down resistors
GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# This callback registers the key that was pressed
# if no other key is currently pressed
def keypadCallback(channel):
    global keypadPressed
    if keypadPressed == -1:
        keypadPressed = channel

# Detect the rising edges on the column lines of the
# keypad. This way, we can detect if the user presses
# a button when we send a pulse.
GPIO.add_event_detect(C1, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C2, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C3, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C4, GPIO.RISING, callback=keypadCallback)

# Sets all lines to a specific state. This is a helper
# for detecting when the user releases a button
def setAllLines(state):
    GPIO.output(L1, state)
    GPIO.output(L2, state)
    GPIO.output(L3, state)
    GPIO.output(L4, state)

def checkSpecialKeys():
    global input
    global cnt
    pressed = False

    GPIO.output(L3, GPIO.HIGH)

    if (GPIO.input(C4) == 1):
        print("\nInput reset!")
        lcd.clear()
        lcd.text("Input reset!",1)
        lcd.text("Enter pin again!",2)
        pressed = True

    GPIO.output(L3, GPIO.LOW)
    GPIO.output(L1, GPIO.HIGH)
    
    if (not pressed and GPIO.input(C4) == 1):
        
        cnt += 1
        
        # checking if the entered pin is the passcode
        if input == secretCode:
            print("\nPin correct!")
            servo.max()
            print("\nDoor unlocked")
            lcd.clear()
            lcd.text("Door unlocked...",1)
            lcd.text("    Welcome!",2)
            buzzer.on()
            greenLED.on()
            time.sleep(1)
            buzzer.off()
            time.sleep(10)
            greenLED.off()
            servo.mid()
            print("\n[INFO] Exiting program")
            cam.release()
            cv2.destroyAllWindows()
            exit()
            
        else:
            print("\nIncorrect pin! Please try again...")
            lcd.clear()
            lcd.text("Incorrect pin!",1)
            lcd.text("Please try again",2)
            # giving three attempts to enter the correct pin
            # or else display the message for intruders
            if cnt > 2 :
                print("\nINTRUDER ALERT!!!")
                print("\nMaximum attempts reached")
                lcd.clear()
                lcd.text("Maximum attempts",1)
                lcd.text("INTRUDER ALERT!!!",2)
                buzzer.beep()
                redLED.on()
                time.sleep(10)
                redLED.off()
                print("\n[INFO] Exiting program")
                cam.release()
                cv2.destroyAllWindows()
                exit()
        
        pressed = True
    GPIO.output(L3, GPIO.LOW)

    if pressed:
        input = ""

    return pressed
                

# reads the columns and appends the value, that corresponds
# to the button, to a variable
def readLine(line, characters):
    global input
    # We have to send a pulse on each line to
    # detect button presses
    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        input = input + characters[0]
    if(GPIO.input(C2) == 1):
        input = input + characters[1]
    if(GPIO.input(C3) == 1):
        input = input + characters[2]
    if(GPIO.input(C4) == 1):
        input = input + characters[3]
    GPIO.output(line, GPIO.LOW)
    
# Function to do tasks after face detection   
def faceDetected() :
    cv2.destroyAllWindows()
    print("\nDoor unlocked")
    lcd.clear()
    lcd.text("Face detected!",1)
    buzzer.on()
    time.sleep(1)
    buzzer.off()
    time.sleep(2)
    servo.max()
    greenLED.on()
    lcd.clear()
    lcd.text("Door unlocked...",1)
    lcd.text("    Welcome!",2)
    time.sleep(10)
    greenLED.off()
    servo.mid()
    print("\n[INFO] Exiting program")
    cam.release()
    cv2.destroyAllWindows()
    exit()
    
def safe_exit(signum, frame):
    exit(1)

signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)
    
    
try :
    while True:
    
        test = 0

        ret, img =cam.read()
        img = cv2.flip(img, -1) # Flip vertically

        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
           )

        for(x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

            # Check if confidence is less than 100 ==> "0" is perfect match 
            if (confidence < 100):
                id = names[id]
                confidence = "  {0}%".format(round(100 - confidence))
                faceDetected()
            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))
        
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
    
        cv2.imshow('Face detection camera',img) 

        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27 or test == 0.33 or time.time() > timeout:
            break
        test = test - 1
    
# keypad passcode entry after face not detected    
    cv2.destroyAllWindows()
    cam.release()
    lcd.clear()
    lcd.text("Face undetected!",1)
    buzzer.on()
    time.sleep(1)
    buzzer.off()
    redLED.on()
    time.sleep(5)
    redLED.off()
    print("\nEnter password:")
    lcd.clear()
    lcd.text("Enter password",1)
    lcd.text("on the keypad",2)
    
    while True :
        # If a button was previously pressed,
        # check, whether the user has released it yet
        if keypadPressed != -1:
            setAllLines(GPIO.HIGH)
            if GPIO.input(keypadPressed) == 0:
                keypadPressed = -1
            else:
                time.sleep(0.1)
        # Otherwise, just read the input
        else:
            if not checkSpecialKeys():
                readLine(L1, ["1","2","3","A"])
                readLine(L2, ["4","5","6","B"])
                readLine(L3, ["7","8","9","C"])
                readLine(L4, ["*","0","#","D"])
                time.sleep(0.1)
            else:
                time.sleep(0.1)

# Do a bit of cleanup
except KeyboardInterrupt:
    print("\n[INFO] Exiting program")
    lcd.clear()
    lcd.text("    Goodbye!",1)
    time.sleep(5)
    cam.release()
    cv2.destroyAllWindows()
    
finally:
    lcd.clear()