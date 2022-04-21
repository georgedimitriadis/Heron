
import time
import threading
import zmq
import os
import signal
import pickle
from Heron.communication.socket_for_serialization import Socket
from Heron import constants as ct
from Heron.communication.ssh_com import SSHCom
from Heron.gui.relic import HeronRelic


class SourceWorker:
    def __init__(self, port, parameters_topic, initialisation_function, end_of_life_function, num_sending_topics,
                 relic_path, ssh_local_ip=' ', ssh_local_username=' ', ssh_local_password=' '):
        self.parameters_topic = parameters_topic
        self.data_port = port
        self.pull_heartbeat_port = str(int(self.data_port) + 1)
        self.initialisation_function = initialisation_function
        self.end_of_life_function = end_of_life_function
        self.num_sending_topics = int(num_sending_topics)
        self.node_name = parameters_topic.split('##')[-2]
        self.node_index = parameters_topic.split('##')[-1]

        self.ssh_com = SSHCom(ssh_local_ip=ssh_local_ip, ssh_local_username=ssh_local_username,
                              ssh_local_password=ssh_local_password)
        self.relic_path = relic_path
        self.import_reliquery()
        self.heron_relic = None

        self.time_of_pulse = time.perf_counter()
        self.port_sub_parameters = ct.PARAMETERS_FORWARDER_PUBLISH_PORT
        self.port_pub_proof_of_life = ct.PROOF_OF_LIFE_FORWARDER_SUBMIT_PORT
        self.running_thread = True
        self.loops_on = True
        self.initialised = False

        self.context = None
        self.socket_push_data = None
        self.socket_sub_parameters = None
        self.stream_parameters = None
        self.thread_parameters = None
        self.parameters = None
        self.socket_pull_heartbeat = None
        self.stream_heartbeat = None
        self.thread_heartbeat = None
        self.socket_pub_proof_of_life = None
        self.thread_proof_of_life = None
        self.index = 0

    def connect_socket(self):
        """
        Sets up the sockets to do the communication with the source_com process through the forwarders
        (for the link and the parameters).
        :return: Nothing
        """
        self.context = zmq.Context()

        # Setup the socket that receives the parameters of the worker_exec function from the node
        self.socket_sub_parameters = Socket(self.context, zmq.SUB)
        self.socket_sub_parameters.setsockopt(zmq.LINGER, 0)
        self.socket_sub_parameters.subscribe(self.parameters_topic)
        self.ssh_com.connect_socket_to_local(self.socket_sub_parameters, r'tcp://127.0.0.1', self.port_sub_parameters)
        self.socket_sub_parameters.subscribe(self.parameters_topic)

        # Setup the socket that pushes the data to the com
        self.socket_push_data = Socket(self.context, zmq.PUSH)
        self.socket_push_data.setsockopt(zmq.LINGER, 0)
        self.socket_push_data.set_hwm(1)
        self.socket_push_data.bind(r"tcp://127.0.0.1:{}".format(self.data_port))

        # Setup the socket that receives the heartbeat from the com
        self.socket_pull_heartbeat = self.context.socket(zmq.PULL)
        self.socket_pull_heartbeat.setsockopt(zmq.LINGER, 0)
        self.ssh_com.connect_socket_to_local(self.socket_pull_heartbeat, r'tcp://127.0.0.1', self.pull_heartbeat_port)

        # Setup the socket that publishes the fact that the worker_exec is up and running to the node com so that it
        # can then update the parameters of the worker_exec.
        self.socket_pub_proof_of_life = Socket(self.context, zmq.PUB)
        self.socket_pub_proof_of_life.setsockopt(zmq.LINGER, 0)
        self.ssh_com.connect_socket_to_local(self.socket_pub_proof_of_life, r'tcp://127.0.0.1',
                                             self.port_pub_proof_of_life, skip_ssh=True)

    def send_data_to_com(self, data):
        self.socket_push_data.send_array(data, copy=False)
        self.index += 1

    def import_reliquery(self):
        # This import is required because it takes a good few seconds to load the package and if the import is done
        # first time in the HeronRelic instance that delays the initialisation of the worker process which can be
        # a problem
        if self.relic_path != '_':
            try:
                import reliquery
                import reliquery.storage
            except ImportError:
                pass

    def relic_create_parameters_df(self, **parameters):
        self._relic_create_df('Parameters', **parameters)

    def relic_create_substate_df(self, **variables):
        self._relic_create_df('Substate', **variables)

    def _relic_create_df(self, type, **variables):
        if self.heron_relic is None:
            self.heron_relic = HeronRelic(self.relic_path, self.node_name, self.node_index)
        if self.heron_relic.operational:
            self.heron_relic.create_the_pandasdf(type, **variables)

    def relic_update_substate_df(self, **variables):
        self.heron_relic.update_the_substate_pandasdf(self.index, **variables)

    def update_parameters(self):
        """
        This updates the self.parameters from the parameters send form the node (through the gui_com)
        If the rlic system is up and running it also saves the new parameters into the Parameters df of the relic
        :return: Nothing
        """
        try:
            topic = self.socket_sub_parameters.recv(flags=zmq.NOBLOCK)
            parameters_in_bytes = self.socket_sub_parameters.recv(flags=zmq.NOBLOCK)
            args = pickle.loads(parameters_in_bytes)
            self.parameters = args
            if not self.initialised and self.initialisation_function is not None:
                self.initialised = self.initialisation_function(self)

            if self.initialised and self.heron_relic is not None and self.heron_relic.operational:
                self.heron_relic.update_the_parameters_pandasdf(parameters=self.parameters, worker_index=self.index)
        except Exception as e:
            pass

    def parameters_loop(self):
        """
        The loop that updates the arguments (self.parameters)
        :return: Nothing
        """
        while self.loops_on:
            self.update_parameters()
            time.sleep(0.2)

    def start_parameters_thread(self):
        """
        Start the thread that runs the infinite arguments_loop
        :return: Nothing
        """
        self.thread_parameters = threading.Thread(target=self.parameters_loop, daemon=True)
        self.thread_parameters.start()

    def heartbeat_loop(self):
        """
        The loop that reads the heartbeat 'PULSE' from the source_com. If it takes too long to receive the new one
        it kills the worker_exec process
        :return: Nothing
        """
        while self.loops_on:
            if self.socket_pull_heartbeat.poll(timeout=(1000 * ct.HEARTBEAT_RATE * ct.HEARTBEATS_TO_DEATH)):
                self.socket_pull_heartbeat.recv()
            else:
                pid = os.getpid()
                self.end_of_life_function()
                self.on_kill(pid)
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
            time.sleep(int(ct.HEARTBEAT_RATE))
        self.socket_pull_heartbeat.close()

    def proof_of_life(self):
        """
        When the worker_exec process starts it sends to the gui_com (through the proof_of_life_forwarder thread) a signal
        that lets the node (in the gui_com process) that the worker_exec is running and ready to receive parameter updates.
        :return: Nothing
        """
        #print('---Sending POL {}'.format('topic = {}, msg = POL'.format(self.parameters_topic.encode('ascii'))))
        for i in range(100):
            try:
                self.socket_pub_proof_of_life.send(self.parameters_topic.encode('ascii'), zmq.SNDMORE)
                self.socket_pub_proof_of_life.send_string('POL')
            except:
                pass
            time.sleep(0.1)

    def start_heartbeat_thread(self):
        """
        Start the heartbeat thread that run the infinite heartbeat_loop
        :return: Nothing
        """
        print('Started Worker {}##{} process with PID = {}'.format(self.node_name, self.node_index, os.getpid()))

        self.thread_heartbeat = threading.Thread(target=self.heartbeat_loop, daemon=True)
        self.thread_heartbeat.start()

        self.thread_proof_of_life = threading.Thread(target=self.proof_of_life, daemon=True)
        self.thread_proof_of_life.start()

    def on_kill(self, pid):
        print('Killing {} {} with pid {}'.format(self.node_name, self.node_index, pid))
        try:
            self.loops_on = False
            self.visualisation_on = False
            self.socket_sub_parameters.close()
            self.socket_push_data.close()
            self.socket_pub_proof_of_life.close()
        except Exception as e:
            print('Trying to kill Source worker {} failed with error: {}'.format(self.node_name, e))
        finally:
            #self.context.term()  # That causes an error
            self.ssh_com.kill_tunneling_processes()



