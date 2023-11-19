import base64
import json
import kivy
kivy.require('2.2.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.network.urlrequest import UrlRequest

import threading

from biometric import enrollment

class LeftLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(LeftLayout, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0.227, 0.525, 1, 1)  # White color for the background
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        label = Label(
            text="Registration",
            font_size=20,
            bold=True,
            color=(1, 1, 1, 1),  # Black color for text
            size_hint=(None, None),
            size=(self.width * 2.3, self.height),  # Adjust the width of the label
            halign='center',
            valign='middle'
        )
        self.add_widget(label)

        label.bind(size=label.setter('text_size'))  # Ensure text fits within label's size

        # Center the label horizontally and vertically within the LeftLayout
        label.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class RightLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(RightLayout, self).__init__(**kwargs)
        
        self.fingerprint = None
        self.finger_captured = Label()
        self.finger_captured.bind(text=self.show_submit)

        self.form_layout = BoxLayout(orientation='vertical', padding=[20, 20, 20, 20], spacing=10)

        
        self.regnum = TextInput(multiline=False, hint_text="Enter Registration Number", size_hint=(1, None), height=40)
        self.regnum.bind(text=self.show_biometric)

        self.form_layout.add_widget(self.regnum)
        
        self.biometric_area = BoxLayout(orientation="vertical")
        
        self.biometric_message = Label(color=(0,0,0,1))
        
        with self.biometric_message.canvas.before:
            Color(0xCA/255.0, 0xF0/255.0, 0xF8/255.0, 1.0)
            self.rect = Rectangle(size=self.biometric_message.size, pos=self.biometric_message.pos)
        
        self.biometric_message.bind(size=self._update_rect, pos=self._update_rect)
        self.biometric_area.add_widget(self.biometric_message)
        

        self.buttons_area = BoxLayout(orientation="vertical")
        self.start_biometric = Button(text='Start Capture', size_hint=(1, None), height=40, padding=[20, 20, 20, 20])
        self.start_biometric.bind(on_press=self.intialize_biometric)
        
        self.submit_button = Button(text='Submit', size_hint=(1, None), height=40, padding=[20, 20, 20, 20])
        self.submit_button.bind(on_press=self.do_submit)
        
        self.form_layout.add_widget(self.buttons_area)

        self.add_widget(self.form_layout)
    
    def show_biometric(self, *args):
        if self.regnum.text.strip():
            if self.biometric_area not in self.form_layout.children:
                self.form_layout.add_widget(self.biometric_area, index=1)
                self.buttons_area.add_widget(self.start_biometric, index=1)
        else:
            if self.biometric_area in self.form_layout.children:
                self.form_layout.remove_widget(self.biometric_area)
                self.buttons_area.remove_widget(self.start_biometric)
    
    def show_submit(self, *args):
        if self.finger_captured == 'capture' and self.submit_button not in self.buttons_area.children:
            self.buttons_area.add_widget(self.submit_button)
        
    def intialize_biometric(self, instance):
        def run_enrollment():
            enrollment(self)
        
        thread = threading.Thread(target=run_enrollment)
        thread.start()
    
    def getserial(self, *args):
        # Extract serial from cpuinfo file
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:6]=='Serial':
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"
        return cpuserial
    
    def do_submit(self, *args):
        # Convert bytearray to Base64
        base64_data = base64.b64encode(self.fingerprint)

        # API endpoint where you want to send the data
        url = 'https://7d3e-197-210-76-53.ngrok-free.app/biometric/enroll'

        # Prepare headers if needed
        headers = {'Content-Type': 'application/json', 'Authorization':self.getserial()}

        # Prepare your payload, including the Base64 data
        payload = {
            'regnum': self.regnum.text,
            'fingerprint': base64_data.decode()  # Convert bytes to string for JSON
        }

        def on_success(req, result):
            self.biometric_message.text = ""
            self.regnum.text = ""
            self.fingerprint = None
            self.finger_captured.text = ""

        def on_failure(req, result):
            self.biometric_message.text = str(result)

        def on_error(req, error):
            self.biometric_message.text = str(error)
        
        # Make a POST request using UrlRequest
        UrlRequest(
            url,
            req_body=json.dumps(payload),
            req_headers=headers,
            method='POST',
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error
        )
        
        
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='horizontal')

        left_layout = LeftLayout(size_hint=(0.3, 1))
        right_layout = RightLayout(size_hint=(0.7, 1))

        layout.add_widget(left_layout)
        layout.add_widget(right_layout)
        return layout

if __name__ == "__main__":
    MyApp(title="AFIT Biometric Enrollment App").run()
