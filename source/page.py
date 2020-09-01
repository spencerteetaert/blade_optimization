import tkinter as tk
from functools import partial

DEFAULT_PACKING_ARGS = {"padx":10, "pady":5}
H1 = {"font":("Arial", 12, "bold"), "padx":20, "pady":10}

class Page:
    def __init__(self, name:str, window:tk.Tk, parent=None):
        self.name = name
        self.parent = parent
        self.window = window

        self.frame = tk.LabelFrame(window, text=name, width=400)
        self.frame.pack()
        if parent is None:
            self.layer = 0
        else:
            self.layer = parent.layer + 1
        
        self.children = [parent]
        self.containers = []

        self.temp_storage = ""

    def __repr__(self):
        to_print = ""
        for i in range(0, self.layer):
            to_print += "- "

        to_print += self.name + "\n"
        
        for i in range(1, len(self.children)):
            to_print += self.children[i].__repr__()

        return to_print

    def add_child(self, to_add):
        self.children += [to_add]
    def add_containers(self, to_adds):
        ''' to_adds is of format [[<widget>, **args]] '''
        for to_add in to_adds:
            self.add_container(to_add[0], to_add[1])
    def add_container(self, to_add, args=DEFAULT_PACKING_ARGS):
        self.containers += [[to_add, args]]

    def go_to_parent(self) -> "Page":
        print("Switching from %s to %s." % (self.name, self.parent.name))
        self.turn_off()
        self.parent.turn_on()
        return self.parent
    def go_to_page(self, destination) -> "Page":
        try:
            destination.turn_on()
            self.turn_off()
            print("Switching from %s to %s." % (self.name, destination.name))
        except:
            print("ERR: Requested page not found.")

    def turn_on(self):
        self.frame.pack()
        for container in self.containers:
            container[0].pack(**container[1])
    def turn_off(self):
        self.frame.pack_forget()
        for container in self.containers:
            container[0].pack_forget()


def switch_pages(current_page, destination):
    current_page.go_to_page(destination)