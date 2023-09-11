def autosize(top):
    top.update()
    top.minsize(0, 0)
    top.update()

def clean(top):
    for x in top.grid_slaves():
        x.grid_forget()
        del x
    return None

def weightfixer(top):
    size = top.grid_size()
    for i in range(size[0]):
        top.columnconfigure(i, weight=1)
    for i in range(size[1]):
        top.rowconfigure(i, weight=1)