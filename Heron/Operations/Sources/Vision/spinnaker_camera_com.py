
import os
from Heron import general_utils as gu

Exec = os.path.realpath(__file__)


# <editor-fold desc="The following code is called from the GUI process as part of the generation of the node.
# It is meant to create node specific elements (not part of a generic node).
# This is where a new nodes individual elements should be defined">

"""
Properties of the generated Node
"""
BaseName = 'Spinnaker Camera'
NodeAttributeNames = ['Parameters', 'Frame Out']
NodeAttributeType = ['Static', 'Output']
ParameterNames = ['Visualisation', 'Cam_Index', 'Pixel Format', 'FPS']
ParameterTypes = ['bool', 'int', 'str', 'float']
ParametersDefaultValues = [False, 0, 'BayerRG8', 120.0]
WorkerDefaultExecutable = os.path.join(os.path.dirname(Exec), 'spinnaker_camera_worker.py')
# </editor-fold>


# <editor-fold desc="The following code is called as its own process when the editor starts the graph">
if __name__ == "__main__":
    spin_camera_com = gu.start_the_source_communications_process()
    spin_camera_com.start_ioloop()
# </editor-fold>
