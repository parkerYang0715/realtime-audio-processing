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
>>> len(x)   
OUTPUT: 4     
>>> import numpy as np    
>>> y=np.frombuffer(x,dtype = np.int16)    
>>> y    
OUTPUT: array([-7720, -5193], dtype=int16)    
>>> len(y)    
OUTPUT: 2    

file2: test_20210907_record_and_playMusic.py   
ref: https://medium.com/geekculture/real-time-audio-wave-visualization-in-python-b1c5b96e2d39     
ref of simpleGUI graph:     
https://www.blog.pythonlibrary.org/2019/10/31/the-demos-for-pysimplegui/      
https://medium.com/geekculture/custom-made-plots-in-python-with-pysimplegui-9f7618fab8d5       
