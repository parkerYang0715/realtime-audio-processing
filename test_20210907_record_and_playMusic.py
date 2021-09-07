import PySimpleGUI as sg
import pyaudio  #record /play stream
import numpy as np
import wave  # read far end wav file
#import simpleaudio as sa  #play music
## RealTime Audio Waveform plot 

# VARS CONSTS:
_VARS = {'window': False,
            'recordStream': False,        # near end recording
            'playStream': False,  # far end playing
            'NearEndData': np.array([]), #near end (plot)  # from recording
            'FarEndData': np.array([]), #far end (plot)       # from wav file
            'errOut': np.array([]),  #AEC output (plot)
            'wf_far': False   #far end wav file object
            }

# pysimpleGUI INIT:
AppFont = 'Any 16'
sg.theme('LightBlue3') # LightBlue3 # DarkBlack  #DarkBlue3
# INIT vars:
CHUNK = 1024  # Samples: 1024,  512, 256, 128
RATE =16000# 44100  # Equivalent to Human Hearing at 40 kHz
INTERVAL = 1  # Sampling Interval in Seconds ie Interval to listen
TIMEOUT = 10  # In ms for the event loop
SIZE_X= CHUNK
SIZE_Y=20000

layout = [[sg.Graph(canvas_size=(800, 600),
                    graph_bottom_left=(-5, -SIZE_Y-1),
                    graph_top_right=(SIZE_X+5, SIZE_Y+1),
                    background_color='white',
                    key='graph')],
                    [sg.ProgressBar(4000, orientation='h',
                    size=(20, 20), key='-PROG-')],
                    [sg.Button('Listen', font=AppFont),
                    sg.Button('Stop', font=AppFont, disabled=True),
                    sg.Button('Exit', font=AppFont)],
                    [sg.Text('Choose wav files',size=(18, 1), font=AppFont)],
                    [sg.Combo(['pno','sp01_speech_16k','sineWav400Hz'], default_value='sp01_speech_16k',size=(16, 1), font=AppFont, key='farendFile') ]
            ]
_VARS['window'] = sg.Window('Mic to waveform plot + Max Level',
                            layout, finalize=True)

graph = _VARS['window']['graph']


pAud = pyaudio.PyAudio()  #for near end playing
farpAud  = pyaudio.PyAudio()  #for far end playing

# FUNCTIONS:

# PYSIMPLEGUI PLOTS
NUMBER_MARKER_FREQUENCY = 100
def drawAxis(dataRangeMin=0, dataRangeMax=100):
    # Y Axis
    #graph.DrawLine((0, 50), (100, 50))
    # X Axis
    #graph.DrawLine((0, dataRangeMin), (0, dataRangeMax))
    
    graph.draw_line((0,0), (SIZE_X, 0))                # axis lines
    graph.draw_line((0, -SIZE_Y), (0, SIZE_Y))
    for x in range(0, SIZE_X+1, NUMBER_MARKER_FREQUENCY):
        graph.draw_line((x, -250), (x, 250))                       # tick marks
        if x < 1000:
            # numeric labels
            graph.draw_text(str(x), (x, -888), color='green')
    #for y in range(-SIZE_Y, SIZE_Y+1, NUMBER_MARKER_FREQUENCY):
    #    graph.draw_line((-3, y), (3, y))
    #    if y != 0:
     #       graph.draw_text(str(y), (-10, y), color='blue')


def stop():
    if _VARS['recordStream']:
        _VARS['recordStream'].stop_stream()
        _VARS['recordStream'].close()
        _VARS['window']['-PROG-'].update(0)
        _VARS['window'].FindElement('Stop').Update(disabled=True)
        _VARS['window'].FindElement('Listen').Update(disabled=False)

    if _VARS['playStream']:
        _VARS['playStream'].stop_stream()
        _VARS['playStream'].close()


def recordCallback(in_data, frame_count, time_info, status):
    _VARS['NearEndData'] = np.frombuffer(in_data, dtype=np.int16)
    return (in_data, pyaudio.paContinue)

def playFarend_Callback(in_data, frame_count, time_info, status):
    data = _VARS['wf_far'].readframes(frame_count)
    _VARS['FarEndData'] = np.frombuffer(data, dtype=np.int16)
    return (data, pyaudio.paContinue)

def listen():
    _VARS['window'].FindElement('Stop').Update(disabled=False)
    _VARS['window'].FindElement('Listen').Update(disabled=True)
    
    _VARS['recordStream'] = pAud.open(format=pyaudio.paInt16,  # prepare for record near end in real time
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=recordCallback)
    
    FARENDfile = values['farendFile']+'.wav'  # prepare for playing far end wav file
    _VARS['wf_far'] = wave.open(FARENDfile, 'rb')
    _VARS['playStream'] = farpAud.open(format=farpAud.get_format_from_width(_VARS['wf_far'].getsampwidth()),# prepare for far end playing
                channels=_VARS['wf_far'].getnchannels(),
                rate=_VARS['wf_far'].getframerate(),
                output=True,
                stream_callback=playFarend_Callback)
                
    _VARS['recordStream'].start_stream()
    _VARS['playStream'].start_stream()


# INIT:

drawAxis()


# MAIN LOOP
while True:
    event, values = _VARS['window'].read(timeout=TIMEOUT)
    if event == sg.WIN_CLOSED or event == 'Exit':
        stop()
        pAud.terminate()
        break
    if event == 'Listen':
        listen()
    if event == 'Stop':
        stop()

    # Along with the global audioData variable, this\
    # bit updates the waveform plot, left it here for
    # explanatory purposes, but could be a method.

    #elif _VARS['NearEndData'].size != 0:
    elif _VARS['FarEndData'].size >100:
        # Update volumne meter
        _VARS['window']['-PROG-'].update(np.amax(_VARS['NearEndData']))  # show near end volumne 
        # Redraw plot
        graph.erase()
        drawAxis()

        # Here we go through the points in the audioData object and draw them
        # Note that we are rescaling ( dividing by 100 ) and centering (+50 )
        # try different values to get a feel for what they do.
          
        for x in range(CHUNK):
            graph.DrawCircle((x, _VARS['NearEndData'][x] ), 0.4, line_color='blue', fill_color='blue' )
        if(_VARS['FarEndData'].size>1023):
            for x in range(CHUNK):
                graph.DrawCircle((x, _VARS['FarEndData'][x] ), 0.4, line_color='red', fill_color='red' )


_VARS['window'].close()
