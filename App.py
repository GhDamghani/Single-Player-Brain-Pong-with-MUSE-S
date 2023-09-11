import tkinter as tk
from sys import exit as sys_exit
import customtkinter as ctk
import tk_lib
from device_setup import device_setup
from game import game
from multiprocessing import freeze_support
if __name__ == "__main__":
    freeze_support()
    app_title = "MUSE BCI Gaming"
    bg_dir = "media/bg.png"
    # icon_dir = "media/UM.ico"
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app_data = {}
    app_data["widget"] = {}

    top = ctk.CTk()
    # top.iconbitmap(default=icon_dir)
    top.option_add("*tearOff", tk.FALSE)

    app_data["widget"]["top"] = top
    app_data["widget"]["top"].title(app_title)
    app_data["widget"]["menu"] = {}


    menubar = tk.Menu(top)
    filemenu = tk.Menu(menubar, tearoff=0)


    def setup_func():
        device_setup(app_data)
    
    def play_func():
        game()


    filemenu.add_command(label="Setup", command=setup_func)
    filemenu.add_command(label="Play", command=play_func)
    filemenu.add_command(label="Close", command=sys_exit)


    menubar.add_cascade(label="Game", menu=filemenu)
    menu_file = tk.Menu(menubar, tearoff=0)
    top.config(menu=menubar)

    app_data["widget"]["menu"]["menubar"] = menubar
    app_data["widget"]["menu"]["filemenu"] = filemenu

    logo = tk.Label(top)
    logo.grid(row=0, column=0, sticky="news")
    
    image = tk.PhotoImage(file=bg_dir)
    logo["image"] = image
    tk_lib.autosize(top)
    tk_lib.weightfixer(top)
    top.mainloop()
