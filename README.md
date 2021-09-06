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
    
Note3: len(data) = 2*len( np.frombuffer(data) )  
