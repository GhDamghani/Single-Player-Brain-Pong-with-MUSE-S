import tkinter as tk
import customtkinter as ctk
from tkinter.ttk import Combobox
import matplotlib.pyplot as plt
import muse_lib
import tk_lib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pylsl import resolve_byprop
from time import sleep, time

from multiprocessing import Process, Pipe

from muse_lib.constants import LSL_EEG_CHUNK, VIEW_SUBSAMPLE

# Set up the game clock
c_connected = '#008000'  # green
c_disconnected = '#ff8080'  # red
c_connecting = '#bfbfbf'  # gray


def search_muse():
    global key_combo, keyvar
    toplevel = tk.Toplevel()
    waiting_label = tk.Label(
        toplevel, text='Searching for Muses, this may take up to 10 seconds...', font=("Arial", 28))
    waiting_label.grid(row=0, column=0, padx=5, pady=5, sticky="news")
    tk_lib.autosize(toplevel)
    tk_lib.weightfixer(toplevel)
    key_combo['values'] = muse_lib.list_muses()
    if key_combo['values']:
        keyvar.set(key_combo['values'][0])
    tk_lib.clean(toplevel)
    toplevel.destroy()


def search_online_streams(name):
    streams = resolve_byprop('type', 'EEG', timeout=5)
    names = [x.name() for x in streams]
    try:
        stream = streams[names.index(name)]
        return stream
    except ValueError:
        return False



def plot_muse(fig_axes):
    available_muse_dict = eval(keyvar.get())
    stream = search_online_streams(name=available_muse_dict['name'])
    finding_flag = False
    if not stream:
        process = Process(target=muse_lib.stream, args=(available_muse_dict['address'],), kwargs={'name': available_muse_dict['name']}) # 
        process.start()
        while stream is False:
            stream = search_online_streams(name=available_muse_dict['name'])
        muse_lib.view(fig_axes=fig_axes, stream=stream)
        return True


def device_setup(app_data):
    top = app_data["widget"]["top"]
    tk_lib.clean(top)

    r, c = 0, 0

    device_frame = ctk.CTkFrame(top)
    device_frame.grid(row=r, column=c, padx=5, pady=5, sticky="news")
    c += 1

    fr, fc = 0, 0

    search_var = tk.StringVar()
    search_B = ctk.CTkButton(
        device_frame, textvariable=search_var, command=lambda: True)
    search_var.set("Search")
    search_B.grid(row=fr, column=fc, padx=5, pady=5, sticky="ns")
    fc += 1

    global key_combo, keyvar
    keyvar = tk.StringVar()
    # keyvar.set("{'name': 'MuseS-3FD0', 'address': '00:55:DA:B9:3F:D0'}")
    key_combo = Combobox(device_frame, textvariable=keyvar,
                         height=1, justify="center")
    key_combo.state(["readonly"])
    key_combo.grid(row=fr, column=fc, padx=5, pady=5, sticky="news")
    fc += 1

    connect_var = tk.StringVar()
    connect_B = ctk.CTkButton(
        device_frame, textvariable=connect_var, command=lambda: True)
    connect_var.set("Plot")
    connect_B.grid(row=fr, column=fc, padx=5, pady=5, sticky="ns")
    connect_B.configure(fg_color=c_disconnected)
    connect_B.configure(state=tk.DISABLED)
    fc += 1

    r += 1
    c = 0
    fig, axes = plt.subplots(1, 1, figsize=(10, 6), sharex=True)

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().grid(row=r, column=c, padx=5, pady=5, sticky="news")
    fig_axes = fig, axes

    search_B.configure(command=search_muse)
    connect_B.configure(command=lambda fig_axes=fig_axes: plot_muse(fig_axes))
    connect_B.configure(state=tk.ACTIVE)

    tk_lib.autosize(top)
    tk_lib.weightfixer(device_frame)
    tk_lib.weightfixer(top)