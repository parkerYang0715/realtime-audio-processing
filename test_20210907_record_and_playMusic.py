import PySimpleGUI as sg
import pyaudio  #record /play stream
import numpy as np
import wave  # read far end wav file
import simpleaudio as sa  #play music
## RealTime Audio Waveform plot 

# VARS CONSTS:
_VARS = {'window': False,
            'stream': False,        # near end recording
            'playStream': False,  # far end playing
            'audioData': np.array([]), #near end (plot)
            'FarEndData': np.array([]), #near end (plot)
            'errOut': np.array([]),  #AEC output (plot)
            'wf_far': False   #far end wav file object
            }

# pysimpleGUI INIT:
AppFont = 'Any 16'
sg.theme('DarkBlue3')
layout = [[sg.Graph(canvas_size=(500, 500),
                    graph_bottom_left=(-2, -2),
                    graph_top_right=(102, 102),
                    background_color='#809AB6',
                    key='graph')],
                    [sg.ProgressBar(4000, orientation='h',
                    size=(20, 20), key='-PROG-')],
                    [sg.Button('Listen', font=AppFont),
                    sg.Button('Stop', font=AppFont, disabled=True),
                    sg.Button('Exit', font=AppFont)],
                    [sg.Text('Choose wav files',size=(18, 1), font=AppFont)],
                    [sg.Combo(['pno','sp01_speech_16k'], default_value='sp01_speech_16k',size=(16, 1), font=AppFont, key='farendFile') ]
            ]
_VARS['window'] = sg.Window('Mic to waveform plot + Max Level',
                            layout, finalize=True)

graph = _VARS['window']['graph']

# INIT vars:
CHUNK = 800#1024  # Samples: 1024,  512, 256, 128
RATE =16000# 44100  # Equivalent to Human Hearing at 40 kHz
INTERVAL = 1  # Sampling Interval in Seconds ie Interval to listen
TIMEOUT = 10  # In ms for the event loop
pAud = pyaudio.PyAudio()  #for near end playing
farpAud  = pyaudio.PyAudio()  #for far end playing

# FUNCTIONS:

# PYSIMPLEGUI PLOTS


def drawAxis(dataRangeMin=0, dataRangeMax=100):
    # Y Axis
    graph.DrawLine((0, 50), (100, 50))
    # X Axis
    graph.DrawLine((0, dataRangeMin), (0, dataRangeMax))

# PYAUDIO STREAM


def stop():
    if _VARS['stream']:
        _VARS['stream'].stop_stream()
        _VARS['stream'].close()
        _VARS['window']['-PROG-'].update(0)
        _VARS['window'].FindElement('Stop').Update(disabled=True)
        _VARS['window'].FindElement('Listen').Update(disabled=False)

    if _VARS['playStream']:
        _VARS['playStream'].stop_stream()
        _VARS['playStream'].close()


def recordCallback(in_data, frame_count, time_info, status):
    _VARS['audioData'] = np.frombuffer(in_data, dtype=np.int16)
    return (in_data, pyaudio.paContinue)

def playFarend_Callback(in_data, frame_count, time_info, status):
    data = _VARS['wf_far'].readframes(frame_count)
    _VARS['FarEndData'] = np.frombuffer(data, dtype=np.int16)
    return (data, pyaudio.paContinue)

def listen():
    _VARS['window'].FindElement('Stop').Update(disabled=False)
    _VARS['window'].FindElement('Listen').Update(disabled=True)
    
    _VARS['stream'] = pAud.open(format=pyaudio.paInt16,  # prepare for record near end in real time
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
                
    _VARS['stream'].start_stream()
    _VARS['playStream'].start_stream()
    #wave_obj = sa.WaveObject.from_wave_file( FARENDfile )    (by simpleaudio)
    #play_obj = wave_obj.play()  #play   (by simpleaudio)
    #print(FARENDfile)


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

    elif _VARS['audioData'].size != 0:
        # Uodate volumne meter
        _VARS['window']['-PROG-'].update(np.amax(_VARS['audioData']))
        # Redraw plot
        graph.erase()
        drawAxis()

        # Here we go through the points in the audioData object and draw them
        # Note that we are rescaling ( dividing by 100 ) and centering (+50 )
        # try different values to get a feel for what they do.
          
        for x in range(CHUNK):
            graph.DrawCircle((x, (_VARS['audioData'][x]/100)+50), 0.4,
                             line_color='blue', fill_color='blue')


_VARS['window'].close()
