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
            time.sleep(2)
        else:
            widget.biometric_message.text = "Place same finger again..."
            time.sleep(2)

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                widget.biometric_message.text = "Fingerprint image taken"
                break
            if i == adafruit_fingerprint.NOFINGER:
                widget.biometric_message.text = "Waiting for finger"
            elif i == adafruit_fingerprint.IMAGEFAIL:
                widget.biometric_message.text = "Fingerprint imaging error"
                return False
            else:
                widget.biometric_message.text = "(1) There was an error capturing fingerprint"
                return False

        widget.biometric_message.text = "Templating fingerprint..."
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            widget.biometric_message.text = "Fingerprint templated"
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                widget.biometric_message.text = "Fingerprint image too messy"
            elif i == adafruit_fingerprint.FEATUREFAIL:
                widget.biometric_message.text = "Could not identify features"
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                widget.biometric_message.text = "Fingerprint image invalid"
            else:
                widget.biometric_message.text = "(2) There was an error capturing fingerprint"
            return False

        if fingerimg == 1:
            widget.biometric_message.text = "Please remove finger"
            time.sleep(2)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    widget.biometric_message.text = "Creating fingerprint model......"
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        widget.biometric_message.text = "Fingerprint model created"
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            widget.biometric_message.text = "Fingerprints did not match"
        else:
            widget.biometric_message.text = "(3) There was an error capturing fingerprint"
        return False

    widget.biometric_message.text = "Storing fingerprint template..."
    data = finger.get_fpdata("char", 1)
    widget.fingerprint = bytearray(data)
    widget.biometric_message.text = "Fingerprint template stored successfully!"
    try:
        widget.finger_captured.text = "capture"
    except:
        pass

    return True