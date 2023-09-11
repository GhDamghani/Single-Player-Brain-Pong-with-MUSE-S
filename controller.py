from multiprocessing.connection import Connection
from multiprocessing import Process, Pipe
import muse_lib
import numpy as np
from scipy.signal import firwin, convolve
# from sklearn.decomposition import FastICA
from time import sleep
from buffer import buffer
from EEGprocessing import preprocess_func, processing_func
import sounddevice as sd
import soundfile as sf

def musicplayer():
    # Load the stereo audio file
    audio_file = "media\\Mus.wav"
    data, sample_rate = sf.read(audio_file)
    while True:
        sd.play(data, sample_rate)
        sd.wait()


def controller(sender_connection: Connection):
    available_muses = muse_lib.list_muses()
    print('Available MUSEs:', available_muses)

    # Can be also selected by the player
    player_muse = available_muses[0]
    print('Selected MUSE:', player_muse)


    stream_receiver, stream_sender = Pipe(duplex=False)
    stream_process = Process(target=muse_lib.stream, args=(player_muse['address'],), kwargs={
                             'name': player_muse['name'], 'sender_connection': stream_sender})
    stream_process.start()


    buffer_window = 1
    decision_window = 0.5

    buffer_receiver, buffer_sender = Pipe(duplex=False)
    buffer_signal_receiver, buffer_signal_sender = Pipe(duplex=False)
    buffer_process = Process(target=buffer, args=(player_muse, buffer_window, buffer_receiver, buffer_sender, buffer_signal_sender))
    buffer_process.start()


    while not (buffer_receiver.poll()):
        pass
    n_chan, sfreq = buffer_receiver.recv()


    preprocessor = preprocess_func(sfreq)

    processor = processing_func(sfreq, decision_window)

    
    while not (stream_receiver.poll()):
        pass
    if stream_receiver.recv() == True:
        sender_connection.send('go')
    print('Stream Signal recieved, GO signal sent')

    musicplayer_process = Process(target=musicplayer)
    musicplayer_process.start()

    update_interval = 0.5
    while True:
        buffer_sender.send(True)

        while not(buffer_signal_receiver.poll()):
            pass
        data, time_ser = buffer_signal_receiver.recv()

        data = preprocessor(data)

        res = processor(data, time_ser)
        print(res)
        sender_connection.send(res)
        sleep(update_interval)
