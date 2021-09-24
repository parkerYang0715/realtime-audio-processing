import PySimpleGUI as sg
import pyaudio  #record /play stream
import numpy as np
import wave  # read far end wav file
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# VARS CONSTS:
_VARS = {'window': False,
            'recordStream': False,        # near end recording
            'playStream': False,  # far end playing
            'NearEndData': np.array([]), #near end (plot)  # from recording
            'FarEndData': np.array([]), #far end (plot)       # from wav file
            'errOut': np.array([]),  #AEC output (plot)
            'wf_far': False,   #far end wav file object
            'fig_agg': False,
            'pltFig': False,
            'ax': False,
            'xData': False,
            'yData': False,
            'Line_far': False,
            'Line_near': False,
            }

# pysimpleGUI INIT:
AppFont = 'Any 16'
sg.theme('LightBlue3') # LightBlue3 # DarkBlack  #DarkBlue3
# INIT vars:
CHUNK = 1024  # Samples: 1024,  512, 256, 128
RATE =16000# 44100  # Equivalent to Human Hearing at 40 kHz
INTERVAL = 1  # Sampling Interval in Seconds ie Interval to listen
TIMEOUT = 20  # In ms for the event loop
SIZE_X= CHUNK
SIZE_Y=32767

layout = [  [sg.Canvas(key='figCanvas')],   # for matplotlib        
                    [sg.ProgressBar(4000, orientation='h',
                    size=(20, 20), key='-PROG-')],
                    [sg.Button('Listen', font=AppFont),
                    sg.Button('Stop', font=AppFont, disabled=True),
                    sg.Button('Exit', font=AppFont)],
                    [sg.Text('Choose wav files',size=(18, 1), font=AppFont),
                     sg.Text('output device',size=(18, 1), font=AppFont)],
                    [sg.Combo(['pno','sp01_speech_16k','sineWav400Hz'], default_value='sp01_speech_16k',
                              size=(16, 1), font=AppFont, key='farendFile')  ,
                     sg.Combo(['3','4','5','6','7'], default_value='5',
                              size=(14, 1), font=AppFont, key='outputID')]
            ]

_VARS['window'] = sg.Window('Microphone Waveform Pyplot',
                            layout, finalize=True,
                            location=(400, 100))




pAud = pyaudio.PyAudio()  #for near end playing
info = pAud.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range (0,numdevices):
    if pAud.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
        print("Input Device id ", i, " - ", pAud.get_device_info_by_host_api_device_index(0,i).get('name'))

    if pAud.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
        print("Output Device id ", i, " - ", pAud.get_device_info_by_host_api_device_index(0,i).get('name'))
farpAud  = pyaudio.PyAudio()  #for far end playing


# \\  -------- PYPLOT -------- //  # for matplotlib
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def drawPlot():
    _VARS['pltFig'] = plt.figure()
    
    #plt.plot(_VARS['xData'], _VARS['yData'], '--k')            # way1
    _VARS['ax'] = _VARS['pltFig'].add_subplot(111)
    _VARS['Line_far'], = _VARS['ax'].plot(_VARS['xData'], _VARS['yData'], '--k')   # way2
    _VARS['Line_near'], = _VARS['ax'].plot(_VARS['xData'], _VARS['yData'], 'r')
    
    plt.ylim(-SIZE_Y, SIZE_Y)
    _VARS['fig_agg'] = draw_figure( _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

def updatePlot(nearend, farend):
    #_VARS['fig_agg'].get_tk_widget().forget()
    #plt.cla()   # Clear axis
    #plt.clf()    # Clears the entire current figure
    #plt.plot(_VARS['xData'],  farend, 'k')  # way1
    _VARS['Line_far'].set_ydata(farend)      # way2
    _VARS['Line_near'].set_ydata(nearend)  # way2
    _VARS['pltFig'].canvas.draw()
    _VARS['pltFig'].canvas.flush_events()
    
    #plt.plot(_VARS['xData'], nearend, '--r')
    #plt.ylim(-SIZE_Y,SIZE_Y)
    #_VARS['fig_agg'] = draw_figure( _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])
# \\  -------- PYPLOT -------- //

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
                output_device_index = int(values['outputID']),
                stream_callback=playFarend_Callback)
                
    _VARS['recordStream'].start_stream()
    _VARS['playStream'].start_stream()



# INIT Pyplot:
plt.style.use('ggplot')     # for matplotlib
_VARS['xData'] = np.linspace(0, CHUNK, num=CHUNK, dtype=int)
_VARS['yData'] = np.zeros(CHUNK)
drawPlot()   # for matplotlib

# MAIN LOOP
while True:
    event, values = _VARS['window'].read(timeout=TIMEOUT)
    if event == sg.WIN_CLOSED or event == 'Exit':
        stop()
        pAud.terminate()
        farpAud.terminate()
        break
    if event == 'Listen':
        listen()
    if event == 'Stop':
        stop()


    #elif _VARS['NearEndData'].size != 0:
    elif _VARS['FarEndData'].size >1020:
        # Update volumne meter
        _VARS['window']['-PROG-'].update(np.amax(_VARS['NearEndData']))  # show near end volumne

        updatePlot(_VARS['NearEndData'],_VARS['FarEndData'])     # for matplotlib   
       

_VARS['window'].close()
