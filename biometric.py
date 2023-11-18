# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import os

import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# If using with Linux/Raspberry Pi and hardware UART:
import serial
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

    

# Test saving files
def enrollment(widget):
    """Take a 2 finger images and template it, then store it in a file"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            widget.biometric_message.text = "Place finger on sensor..."
            time.sleep(1)
        else:
            widget.biometric_message.text = "Place same finger again..."
            time.sleep(1)

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                widget.biometric_message.text = "Fingerprint image taken"
                time.sleep(1)
                break
            if i == adafruit_fingerprint.NOFINGER:
                widget.biometric_message.text = "Waiting for finger"
                time.sleep(1)
            elif i == adafruit_fingerprint.IMAGEFAIL:
                widget.biometric_message.text = "Fingerprint imaging error"
                time.sleep(1)
                return False
            else:
                widget.biometric_message.text = "(1) There was an error capturing fingerprint"
                time.sleep(1)
                return False

        widget.biometric_message.text = "Templating fingerprint..."
        time.sleep(1)
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            widget.biometric_message.text = "Fingerprint templated"
            time.sleep(1)
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                widget.biometric_message.text = "Fingerprint image too messy"
                time.sleep(1)
            elif i == adafruit_fingerprint.FEATUREFAIL:
                widget.biometric_message.text = "Could not identify features"
                time.sleep(1)
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                widget.biometric_message.text = "Fingerprint image invalid"
                time.sleep(1)
            else:
                widget.biometric_message.text = "(2) There was an error capturing fingerprint"
                time.sleep(1)
            return False

        if fingerimg == 1:
            widget.biometric_message.text = "Please remove finger"
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    widget.biometric_message.text = "Creating fingerprint model......"
    time.sleep(1)
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        widget.biometric_message.text = "Fingerprint model created"
        time.sleep(1)
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            widget.biometric_message.text = "Fingerprints did not match"
            time.sleep(1)
        else:
            widget.biometric_message.text = "(3) There was an error capturing fingerprint"
            time.sleep(1)
        return False

    widget.biometric_message.text = "Storing fingerprint template..."
    time.sleep(1)
    data = finger.get_fpdata("char", 1)
    with open(f"{widget.regnum.text}.dat", "wb") as file:
        file.write(bytearray(data))
    widget.biometric_message.text = f"Fingerprint template stored as {widget.regnum.text}.dat."
    widget.finger_captured.text = "capture"
    time.sleep(1)

    return True