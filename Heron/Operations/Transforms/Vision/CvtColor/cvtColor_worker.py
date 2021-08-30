
import sys
from os import path
import cv2
import numpy as np

current_dir = path.dirname(path.abspath(__file__))
while path.split(current_dir)[-1] != r'Heron':
    current_dir = path.dirname(current_dir)
sys.path.insert(0, path.dirname(current_dir))

from Heron.communication.socket_for_serialization import Socket
from Heron import general_utils as gu
from Heron.Operations.Transforms.Vision.CvtColor import cvtColor_com
from Heron.communication.transform_worker import TransformWorker

worker_object: TransformWorker


def cvtColor(data, parameters):
    global worker_object

    try:
        worker_object.visualisation_on = parameters[0]
        color_conv_string = parameters[1]
    except:
        worker_object.visualisation_on = cvtColor_com.ParametersDefaultValues[0]
        color_conv_string = cvtColor_com.ParametersDefaultValues[1]

    message = data[1:]  # data[0] is the topic
    image = Socket.reconstruct_array_from_bytes_message_cv2correction(message)
    try:
        worker_object.worker_visualisable_result = cv2.cvtColor(image, getattr(cv2, color_conv_string))
    except Exception as e:
        worker_object.worker_visualisable_result = np.array((10, 10))
        print('cvtColor {} operation failed with exception {}'.format(worker_object.node_index, e))

    worker_object.visualisation_loop_init()

    return [worker_object.worker_visualisable_result]


def on_end_of_life():
    pass


if __name__ == "__main__":
    worker_object = gu.start_the_transform_worker_process(cvtColor, on_end_of_life)
    worker_object.start_ioloop()
