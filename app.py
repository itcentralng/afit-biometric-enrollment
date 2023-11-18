import kivy
kivy.require('2.2.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle

import threading

from biometric import enrollment

class LeftLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(LeftLayout, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0.89, 0.9, 0.76, 1)  # White color for the background
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        label = Label(
            text="Registration",
            font_size=20,
            bold=True,
            color=(0, 0, 0, 1),  # Black color for text
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

        with self.canvas.before:
            Color(0.97, 0.97, 0.95, 1)  # Background color F7F7F2 in RGB
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        self.form_layout = BoxLayout(orientation='vertical', padding=[20, 20, 20, 20], spacing=10)

        
        self.regnumlabel = Label(text='REGNUM', color='grey', halign='left')
        self.regnum = TextInput(multiline=False, width=200)
        

        
        self.form_layout.add_widget(self.regnumlabel)
        self.form_layout.add_widget(self.regnum)
        
        self.biometric_area = BoxLayout()
        self.start_biometric = Button(text='Start Capture')
        self.start_biometric.bind(on_press=self.intialize_biometric)
        self.biometric_message = Label()
        self.biometric_area.add_widget(self.start_biometric)
        self.biometric_area.add_widget(self.biometric_message)

        self.fingerprint_button = Button(text='Capture Fingerprint')
        self.fingerprint_button.bind(on_press=self.show_fingerprint_popup)
        self.form_layout.add_widget(self.fingerprint_button)

        self.add_widget(self.form_layout)
        self.biometric_popup = Popup(title='Biometric Capture', content=self.biometric_area, size_hint=(0.9, 0.9))
    
    def intialize_biometric(self, instance):
        def run_enrollment():
            enrollment(self)
        
        thread = threading.Thread(target=run_enrollment)
        thread.start()
    
    def show_fingerprint_popup(self, instance):
        if self.regnum.text:
            self.biometric_popup.open()

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
