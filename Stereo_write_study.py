## ---PyAudio Example: Play a wave file (callback version)---
import numpy as np
import pyaudio
import wave
import time
import sys
#playFile = 'pno.wav'
#playFile = 'dream_16k_cut_stereo.wav'
#playFile = 'dream_16k_cut_mono.wav'
playFile = 'mix_stereo_8k.wav'

wf = wave.open(playFile , 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# define callback (2)
def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)  # = ch1[0],ch2[0], ch1[1],ch2[1] , ... , ch1[1023],ch2[1023]
    ch = np.frombuffer(data, dtype=np.int16)
    print(type(data))  # <class 'bytes'>
    print(type(ch))     # <class 'numpy.ndarray'>
    #print(len(data))  #4096  # stereo
    #print(len(ch))     #2048  # stereo
    #print(ch[0])   # = ch1[0]
    #print(ch[1])   # = ch2[0]
    #print(ch[2])   # = ch1[1]
    #print(ch[3])   # = ch2[1]
    #print(ch[4])   # = ch1[2]
    #print(ch[5])   # = ch2[2]

    #print(len(data))  # stereo 4096  # mono 2048 
    return (data, pyaudio.paContinue)

# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)

print(wf.getnchannels())
print(wf.getframerate())
# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio (7)
p.terminate()
