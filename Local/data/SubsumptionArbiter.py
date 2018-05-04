from InitialisationTask import InitialisationTask
from DaytimeAttentionTask import DaytimeAttentionTask
from StressReductionTask import StressReductionTask
from DisconnectionTask import DisconnectionTask

from threading import Thread
import time

class SubsumptionArbiter():
    def __init__(self, display_manager, audio_manager):
        
        self.tasks = []
        self.display_manager = display_manager
        self.audio_manager = audio_manager
        
    def setup_tasks(self):
        init_task = InitialisationTask(self.display_manager, self.audio_manager)
        self.tasks.append(init_task)
        
        daytime_attention_task = DaytimeAttentionTask(self.display_manager, self.audio_manager)
        self.tasks.append(daytime_attention_task)
        
        stress_reduction_task = StressReductionTask(self.display_manager, self.audio_manager)
        self.tasks.append(stress_reduction_task)
        
        disconnection_task = DisconnectionTask(self.display_manager, self.audio_manager)
        self.tasks.append(disconnection_task)
        
    def start_threads(self):
        # Starts up the background threads of the tasks, and of the arbiter itself
        
        for task in self.tasks:
            task.start_task_thread()
        
        arbiter_thread = Thread(target=self.arbiter_thread)
        arbiter_thread.daemon = True
        arbiter_thread.start()
        
    def arbiter_thread(self):
        while True:
            
            # Iterate through our tasks backwards.
            # If one subsumes, update a flag to mask the output of the other tasks.
            
            did_subsume = False
            for task in reversed(self.tasks):
                subsumes = task.wants_subsumption()
                
                if subsumes is True and did_subsume is False:
                    task.set_is_outputting(True)
                    did_subsume = True
                else:
                    task.set_is_outputting(False)
            
            # Slow down the looping
            time.sleep(0.05)
            
            
    def on_mqtt_message(self, topic, message):
        for task in self.tasks:
            task.on_mqtt_message(topic, message)