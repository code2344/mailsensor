from machine import Pin, ADC
import time

# ---------------- PINS ----------------
fsr = ADC(Pin(2))  # P0.02

reed1 = Pin(3, Pin.IN, Pin.PULL_UP)
reed2 = Pin(28, Pin.IN, Pin.PULL_UP)
reed3 = Pin(29, Pin.IN, Pin.PULL_UP)

# ---------------- SETTINGS ----------------
FSR_THRESHOLD = 3000      # adjust after calibration
DOOR_OPEN_TIMEOUT = 10    # seconds

# ---------------- STATE ----------------
last_fsr = fsr.read_u16()
door_open_time = None

mail_event = False
tamper_event = False


# ---------------- FUNCTIONS ----------------

def is_door_open():
    # assumes reed closes to GND when magnet present
    # adjust if your wiring is inverted
    return (reed1.value() == 1 or
            reed2.value() == 1 or
            reed3.value() == 1)


def read_fsr():
    return fsr.read_u16()


def reset_events():
    global mail_event, tamper_event
    mail_event = False
    tamper_event = False


# ---------------- MAIN LOOP ----------------

while True:
    door = is_door_open()
    value = read_fsr()
    now = time.time()

    # ---------------- DOOR TIMING ----------------
    if door:
        if door_open_time is None:
            door_open_time = now
    else:
        door_open_time = None

    # ---------------- WEIGHT CHANGE ----------------
    if abs(value - last_fsr) > FSR_THRESHOLD:
        if not door:
            tamper_event = True  # weight changed without door open
        else:
            mail_event = True    # normal mail activity

        last_fsr = value

    # ---------------- DOOR LEFT OPEN ----------------
    if door and door_open_time is not None:
        if now - door_open_time > DOOR_OPEN_TIMEOUT:
            tamper_event = True  # suspicious prolonged access

    # ---------------- OUTPUT STATUS ----------------
    if mail_event:
        print("MAIL EVENT detected")

    if tamper_event:
        print("TAMPER ALERT detected")

    # optional: continuous debug
    # print(value, door)

    time.sleep(0.1)
