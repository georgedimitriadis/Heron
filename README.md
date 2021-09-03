# Heron

## Introduction

Heron is a Python only graphical editor designed to initiate, connect and orchestrate multiple processes, potentially running on multiple computers. Each process is graphically represented as a node with inputs and outputs. Connecting an output of one process to the input of another will result in the data generated by the output process to be passed to the input one, subsequently triggering the input processes functionality.

Heron has originally been conceptualised as a framework to allow modular and fast experimental setup. It is designed to connect multiple pieces of hardware with analysis and data collection code in a versatile / experiment specific matter. Its main goal is to abstract away the need to pass data through the different parts of a pipeline with specific data collection and on the fly analysis requirements, an effort which more often than not, results in single use, spaghetti code.

Heron is not another visual programming language. It is just a graphical abstraction of the way individual pieces of code, each running in its own process, communicate with each other in an experimental pipeline. The code that does the actual work is Python code and the user is expected to construct their own pieces of code (that can be trivially wrapped into the code necessary to have them represented as Heron nodes).

Here is an example of the Heron editor running a simple pipeline


![Heron at work](https://user-images.githubusercontent.com/12892531/124310304-e7139e80-db63-11eb-8640-40b23746dfbb.png)

More information on the parts of the Heron editor and its use see the Use paragraph.


## Installation

Heron does not require any type of installation (and thus it has not yet been packaged into pip or conda - something that will happen in the future). Just download the repo, put it somewhere and then run the editor.py script found in the Heron/Heron/gui folder.

Important note. The whole of the Heron repo must be found in all the computers that run nodes in a pipeline. The editor will only run in one of the computers but the whole repo needs to be present in all computers (since this defines Heron's communication protocol). Any code that runs in a machine separate to the computer running the editor must be part of the Heron directory structure wrapped appropriately in the code that creates the Heron nodes.


## Requirements. 

The library requirements of Heron are:

pyzmq >= 22.x

numpy

dearpygui = 0.8.xx

opencv = 4.x (3.x should work but not tested)

paramikro (required if the multiple computers fuctionality is utilised)

pynput (for the user input nodes)

diskarray (for the save numpy node)

If you use conda then dearpygui and diskarray have to be installed by pip (no conda packages yet). 
Trying to install diskarray will try to install numpy (on top of the conda install numpy). Do not do that! First "pip install basescript" (a diskarray requirement) and then "pip install diskarray --no-dependencies" which will install only diskarray.


## Use

The left hand side table in the editor is a list of all available nodes. The user clicks on the ones they need and then proceeds to connect the outputs to the inputs and sets up the parameters values. Once this is done, the user starts the Graph that has been generated. The result is the initialisation of a series of processes (double the number of nodes plus one) which then pass data between them as the connectivity of their nodes prescribes.

There are three types of nodes:

The Source nodes which are meant to bring data from the outside world into the pipeline. Examples of these are cameras, microphones, data acquisition devices and in general any type of hardware that will generate data. For example, in the pipeline shown above, there is a single Source node live capturing camera frames. Source nodes have only outputs.

Then there are the Transform nodes which grab data from one of their inputs, transform it and then pass it to their output. Heron supports both one output to one input and one output to many inputs connectivity. It also supports Nodes with multiple inputs and multiple outputs. In the above example, each captured frame is passed through a canny filter.

Finally there are Sink nodes which only have inputs and which are meant as final saving points for the data. In the above example this is the Save FFMPEG video which takes the canny transformed frame and adds it to a video file (through running ffmpeg).

In the future there will be Kernel nodes with no inputs or outputs (self sufficient processes that do stuff without requiring input or generating output).

## Heron protocol

The below picture gives the overview of the communication protocol Heron uses.

![Heron-data-diagram](https://user-images.githubusercontent.com/12892531/124312326-065ffb00-db67-11eb-9fe5-9ed214d6d930.png)


