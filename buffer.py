from pylsl import resolve_byprop, StreamInlet
from muse_lib.constants import LSL_EEG_CHUNK
import numpy as np

def search_online_streams(name):
    streams = resolve_byprop('type', 'EEG', timeout=5)
    names = [x.name() for x in streams]
    try:
        stream = streams[names.index(name)]
        return stream
    except ValueError:
        return False

def buffer(player_muse, window, reciever, sender, sender_signal):
    stream = search_online_streams(name=player_muse['name'])
    while stream is False:
        stream = search_online_streams(name=player_muse['name'])
    print(f"Stream with name {player_muse['name']} was found")
    inlet = StreamInlet(stream, max_chunklen=LSL_EEG_CHUNK)
    info = inlet.info()
    description = info.desc()
    ch = description.child('channels').first_child()
    ch_names = [ch.child_value('label')]
    n_chan = 4  # info.channel_count()
    for i in range(n_chan):
        ch = ch.next_sibling()
        ch_names.append(ch.child_value('label'))
    # print('Channel Names:', ch_names) # 'TP9', 'AF7', 'AF8', 'TP10'
    sfreq = info.nominal_srate()
    n_samples = int(sfreq * window)
    buffer_data = np.zeros((n_samples, n_chan))
    time_ser = np.arange(-window, 0, 1. / sfreq)
    dejitter = True

    print(f'Information about this stream: n_chan: {n_chan}\twindow: {window}\tn_samples: {n_samples}\tsfreq: {sfreq}')

    sender.send((n_chan, sfreq))

    while True:
        samples, timestamps = inlet.pull_chunk(timeout=1.0,
                                               max_samples=LSL_EEG_CHUNK)
        samples = np.array(samples)[:, :n_chan]
        if timestamps:
            if dejitter:
                timestamps_l = len(timestamps)
                timestamps = np.float64(np.arange(timestamps_l))
                timestamps /= sfreq
                timestamps += time_ser[-1] + 1. / sfreq
            time_ser = np.concatenate([time_ser, timestamps])
            time_ser = time_ser[-n_samples:]

            buffer_data = np.vstack([buffer_data, samples])
            buffer_data = buffer_data[-n_samples:]
            buffer_data[np.isnan(buffer_data)] = 0
        if reciever.poll():
            if reciever.recv() == True:
                sender_signal.send((buffer_data, time_ser))