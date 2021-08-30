
import sys
from os import path
import time
import numpy as np

current_dir = path.dirname(path.abspath(__file__))
while path.split(current_dir)[-1] != r'Heron':
    current_dir = path.dirname(current_dir)
sys.path.insert(0, path.dirname(current_dir))

from Heron import general_utils as gu
from Heron.Operations.Sources.Input.Key_Press import key_press_com
from Heron.communication.source_worker import SourceWorker
from pynput.keyboard import Listener

worker_object: SourceWorker
listener: Listener
key_pressed_and_released = [None, None]
previous_user_input = False
loop_on = True
new_input_for_vis = ''

def on_key_pressed(key):
    global key_pressed_and_released
    try:
        key_pressed_and_released[0] = key.char
    except:
        pass


def on_key_released(key):
    global key_pressed_and_released
    global previous_user_input
    global new_input_for_vis

    try:
        key_pressed_and_released[1] = key.char
        new_input_for_vis = key.char
    except:
        new_input_for_vis = 'No special keys please'


def visualisation_to_stdout():
    global worker_object
    global previous_user_input
    global key_pressed_and_released
    global new_input_for_vis

    while True:
        while worker_object.visualisation_on:
            if new_input_for_vis:
                print(new_input_for_vis)
                if new_input_for_vis == worker_object.worker_visualisable_result:
                    print('Outputing :{}'.format(worker_object.worker_visualisable_result))
                new_input_for_vis = False


def start_key_press_capture(_worker_object):
    global worker_object
    global key_pressed_and_released
    global listener
    global loop_on

    worker_object = _worker_object
    worker_object.set_new_visualisation_loop(visualisation_to_stdout)
    listener = Listener(on_press=on_key_pressed, on_release=on_key_released)
    listener.start()

    while loop_on:
        try:
            waiting_for_key = str(worker_object.parameters[1])
        except:
            waiting_for_key = key_press_com.ParametersDefaultValues[1]

        if key_pressed_and_released[0] == waiting_for_key and \
           key_pressed_and_released[1] == waiting_for_key:
            worker_object.worker_visualisable_result = np.array([waiting_for_key])
            worker_object.socket_push_data.send_array(worker_object.worker_visualisable_result, copy=False)
            key_pressed_and_released = [None, None]
        try:
            worker_object.visualisation_on = worker_object.parameters[0]
        except:
            worker_object.visualisation_on = key_press_com.ParametersDefaultValues[0]

        worker_object.visualisation_loop_init()
        time.sleep(0.1)


def on_end_of_life():
    global listener
    global loop_on
    loop_on = False
    try:
        listener.stop()
    except:
        pass


if __name__ == "__main__":
    gu.start_the_source_worker_process(start_key_press_capture, on_end_of_life)