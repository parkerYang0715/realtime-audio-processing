## convert byte array to int array when using pyaudio  
## REF: https://github.com/chipmuenk/A2SRC/blob/master/A2SRC/pyaudio_numpy_example.py

import pyaudio
import numpy as np
from scipy import signal

np_type = np.int16

CHUNK = 2048
WIDTH = 2
CHANNELS = 2
RATE = 16000
RECORD_SECONDS =13

p = pyaudio.PyAudio()

delay_b = np.zeros(361)
delay_b[0]=1
delay_b[180]=0.8
delay_b[360]=0.6

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

print("* recording")

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)   # Notice: len(data) = 2*len(  np.frombuffer(data)  )
    #print('len(data)=' + str(len(data)))
    # stereo: len(data) = 8292 #mono: len(data) = 4096
    # read CHUNK frames to string and convert to numpy array:
    samples_in2 = np.frombuffer(data, dtype=np_type)    #way 2
    # get ch1 data
    samples_in2 = samples_in2[::2]
    outData = signal.lfilter(delay_b, [1], samples_in2 ).astype(np.int16)
    
    #outData = outData.astype(np.int16) 
    #print(len(outData))
    #print(outData[5:25])
    #outData = np.chararray.tobytes(outData.astype(np_type))

    freq_hz = 360.0
    duration_s = 3.0

    t_samples = np.arange(CHUNK)
    waveform = np.sin(2 * np.pi * freq_hz * t_samples / RATE)
    waveform *= 0.6
    waveform= np.int16(waveform * 32767)
    #print(len(waveform))

    data = np.zeros(2*CHUNK).astype(np.int16)
    data[::2]=outData 
    data[1::2]=waveform 
    data = np.chararray.tobytes(data.astype(np.int16))
    
    stream.write(data, CHUNK)

print("* done")

stream.stop_stream()
stream.close()

p.terminate()
