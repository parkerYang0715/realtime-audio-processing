file1: record_and_play_stream_limitedTime.py    (record a few samples and add echo effect then play them back in real-time)
ref:  
https://people.csail.mit.edu/hubert/pyaudio/#examples  ( play / record by Pyaudio )      
Note1: the pyaudio library returns "bytes"  instead of int array like sounddevice!!!     
Note2: you need to convert the data type to handle it with DSP skills  
eg.     
    data = stream.read(CHUNK)     # type "bytes"      
    #samples_in = np.fromstring(data, dtype=np_type)    #way 1  # type "numpy int array"    
    samples_in2 = np.frombuffer(data, dtype=np_type)    #way 2  # type "numpy int array"   
    outData = signal.lfilter(delay_b, [1], samples_in2 )  # filter   
    #outData = outData.astype(np.int16)    
    outData = np.chararray.tobytes(outData.astype(np_type))  # convert the data type back to "bytes"     
    -7720
Note3: len(data) = 2*len( np.frombuffer(data) )  
eg.     
x = b'\xd8\xe1\xb7\xeb'   
len(x)   
OUTPUT: 4     
import numpy as np    
y=np.frombuffer(x,dtype = np.int16)    
y    
OUTPUT: array([-7720, -5193], dtype=int16)    
len(y)    
OUTPUT: 2    
   
file2: test_20210907_record_and_playMusic.py   
ref: https://medium.com/geekculture/real-time-audio-wave-visualization-in-python-b1c5b96e2d39     
ref of simpleGUI graph:     
https://www.blog.pythonlibrary.org/2019/10/31/the-demos-for-pysimplegui/      
https://medium.com/geekculture/custom-made-plots-in-python-with-pysimplegui-9f7618fab8d5       
     
file3: test_20210907_record_and_playMusic_v2.py   (improve the matplot update method based on the following ref.)     
ref: https://www.geeksforgeeks.org/how-to-update-a-plot-in-matplotlib/  


how to write output to pyaudio for stereo    
data = wf.readframes(frame_count)  # = ch1[0],ch2[0], ch1[1],ch2[1] , ... , ch1[1023],ch2[1023]     
ch = np.frombuffer(data, dtype=np.int16)    
#print(type(data))  # <class 'bytes'>    
#print(type(ch))     # <class 'numpy.ndarray'>   
#print(len(data))  #4096  # stereo   
#print(len(ch))     #2048  # stereo   
#print(ch[0])   # = ch1[0]     
#print(ch[1])   # = ch2[0]     
#print(ch[2])   # = ch1[1]     
#print(ch[3])   # = ch2[1]      
#print(ch[4])   # = ch1[2]     
#print(ch[5])   # = ch2[2]   

# Device setting   
pAud = pyaudio.PyAudio()  #for near end playing
pAud.get_default_output_device_info()   
info = pAud.get_host_api_info_by_index(0)   
numdevices = info.get('deviceCount')    
for i in range (0,numdevices):    
&nbsp;&nbsp;if pAud.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:   
&nbsp;&nbsp;&nbsp;&nbsp;print("Input Device id ", i, " - ", pAud.get_device_info_by_host_api_device_index(0,i).get('name'))   
  
&nbsp;&nbsp;if pAud.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:     
&nbsp;&nbsp;&nbsp;&nbsp;print("Output Device id ", i, " - ", pAud.get_device_info_by_host_api_device_index(0,i).get('name'))       

ref: https://people.csail.mit.edu/hubert/pyaudio/docs/#class-stream
PA_manager – A reference to the managing PyAudio instance   
rate – Sampling rate   
channels – Number of channels   
format – Sampling size and format. See PortAudio Sample Format.   
input – Specifies whether this is an input stream. Defaults to False.   
output – Specifies whether this is an output stream. Defaults to False.   
input_device_index – Index of Input Device to use. Unspecified (or None) uses default device. Ignored if input is False.   
output_device_index – Index of Output Device to use. Unspecified (or None) uses the default device. Ignored if output is False.   
frames_per_buffer – Specifies the number of frames per buffer.   
