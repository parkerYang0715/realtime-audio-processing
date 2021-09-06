## convert byte array to int array when using pyaudio  
## REF: https://github.com/chipmuenk/A2SRC/blob/master/A2SRC/pyaudio_numpy_example.py

import pyaudio
import numpy as np
from scipy import signal

np_type = np.int16

CHUNK = 2048
WIDTH = 2
CHANNELS = 1
RATE = 16000
RECORD_SECONDS =10

p = pyaudio.PyAudio()

delay_b = np.zeros(361)
delay_b[0]=1
delay_b[360]=0.95

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

print("* recording")

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)   # Notice: len(data) = 2*len(  np.frombuffer(data)  )
    # read CHUNK frames to string and convert to numpy array:
    #samples_in = np.fromstring(data, dtype=np_type)    #way 1 
    samples_in2 = np.frombuffer(data, dtype=np_type)    #way 2 
    outData = signal.lfilter(delay_b, [1], samples_in2 )
    #outData = outData.astype(np.int16) 
    #print(len(outData))
    #print(outData[5:25])
    outData = np.chararray.tobytes(outData.astype(np_type))
    stream.write(outData, CHUNK)

print("* done")

stream.stop_stream()
stream.close()

p.terminate()
