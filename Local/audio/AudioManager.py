import os, sys, subprocess, time

from threading import Thread

import pyaudio, wave
import random

try:
    import pkg_resources
    scriptspath = pkg_resources.resource_filename(__name__, 'scripts')
    tracks_path = pkg_resources.resource_filename(__name__, 'tracks')
except:
    import os.path as p
    scriptspath = p.join(p.dirname(p.abspath(__file__)), 'scripts')
    tracks_path = p.join(p.dirname(p.abspath(__file__)), 'tracks')

class AudioManager():
    def __init__(self, is_emulated):
        
        self.speaker_connected = False
        self.is_emulated = is_emulated
        
        self.current_playlist = self.PLAYLIST_NONE
        self.track_pointer = 0
        self._skip_to_next = False
        self.tracks = []
        
    #########################################################################
    # Speaker connectivity handling
    #########################################################################
        
    def setup(self):
        # Start the thread that monitors for Bluetooth speaker connectivity.
        connection_thread = Thread(target=self._speaker_connection_thread)
        connection_thread.daemon = True
        connection_thread.start()
        
        playback_thread = Thread(target=self._playback_thread)
        playback_thread.daemon = True
        playback_thread.start()
        
    def _connect_to_speaker(self):
        while True:
            status = subprocess.call('ls /dev/input/event0 2>/dev/null', shell=True)
        
            if status == 0:
                print("[INFO] Speaker is connected")
                self.speaker_connected = True
                time.sleep(2)
            elif status == 2:
                print("[WARN] Speaker is NOT connected")
                self.speaker_connected = False
                
                # Attempt a connection
                subprocess.call(scriptspath + '/mrt_autopair.sh', shell=True)
                time.sleep(2)
                
    def _connect_to_speaker_emulated(self):
        # No need to wait on a connection to internal speakers!
        time.sleep(3)
        print("[INFO] Speaker is connected")
        self.speaker_connected = True
        
    def _speaker_connection_thread(self):
        if self.is_emulated is True:
            self._connect_to_speaker_emulated()
        else:
            self._connect_to_speaker()
        
    def has_connected_speaker(self):
        return self.speaker_connected
        
    #########################################################################
    # Audio control
    #########################################################################
    
    @property
    def PLAYLIST_STUDY_AMBIENCE(self):
        return 0
        
    @property
    def PLAYLIST_DE_STRESS(self):
        return 1
        
    @property
    def PLAYLIST_NONE(self):
        return -1
    
    def request_playlist(self, playlist):
        # Don't start a playlist that's already running        
        if playlist == self.current_playlist:
            return
            
        # Start the playlist
        self._start_playlist(playlist)
            
    def _start_playlist(self, playlist):            
        # 1. Read the list of tracks for the requested playlist, and randomise them
        
        path = ""
        
        print("[DEBUG] Starting playlist: " + str(playlist))
            
        if playlist is self.PLAYLIST_DE_STRESS:
            path = tracks_path + "/de-stress/"
        elif playlist is self.PLAYLIST_STUDY_AMBIENCE:
            path = tracks_path + "/study-ambience/"
        elif playlist is self.PLAYLIST_NONE:
            path = tracks_path + "/none/"
        
        track_listing = os.listdir(path)
        if track_listing is None: track_listing = []
        
        try:
            track_listing.remove("licenses.txt")
            track_listing.remove(".DS_Store")
        except:
            pass
            
        random.shuffle(track_listing)
        
        # 2. Load .wav files
        self.tracks = []
        for track in track_listing:
            filename = path + "/" + track
            
            wf = wave.open(filename, 'rb')
            
            self.tracks.append(wf)
        
        # 3. Reset the track pointer and playlist value
        should_skip = self.current_playlist is not playlist
        self.track_pointer = 0
        self.current_playlist = playlist
        
        # 4. Request the playback thread to start the next track
        self._skip_to_next = should_skip
            
    def _playback_thread(self):
        audio = pyaudio.PyAudio()
        
        while True:
            if self.speaker_connected == False:
                # No point playing anything!
                time.sleep(0.02) # Slow down execution
                continue
            
            if self.current_playlist is self.PLAYLIST_NONE or len(self.tracks) == 0:
                time.sleep(0.02) # Slow down execution
                continue
                
            # Read next track from the track pointer and internal list
            wf = self.tracks[self.track_pointer]
            
            print("[DEBUG] Playing track: " + str(self.track_pointer))
            
            # Setup data
            stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
                            
            CHUNK = 1024
            data = wf.readframes(CHUNK)

            # Output audio
            while data != '' and self._skip_to_next is False:
                stream.write(data)
                data = wf.readframes(CHUNK)

            stream.stop_stream()
            stream.close()
            
            # Reset skip variable
            last_skip = self._skip_to_next
            self._skip_to_next = False
            
            # Don't advance the track pointer if we just skipped!
            if last_skip is False:
                self.track_pointer += 1
                if self.track_pointer >= len(self.tracks):
                    # Restart the current playlist with a new shuffled ordered
                    self._start_playlist(self.current_playlist)
            
        audio.terminate()