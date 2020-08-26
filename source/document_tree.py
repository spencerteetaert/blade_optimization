import tkinter as tk
from functools import partial

DEFAULT_PACKING_ARGS = {"padx":10, "pady":5}

class Page:
    def __init__(self, name:str, window:tk.Tk, parent=None):
        self.name = name
        self.parent = parent
        self.window = window

        self.frame = tk.Frame(window)
        self.frame.pack()
        if parent is None:
            self.layer = 0
        else:
            self.layer = parent.layer + 1
        
        self.children = [parent]
        self.containers = []

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
            self.add_containter(to_add[0], to_add[1])
    def add_containter(self, to_add, args=DEFAULT_PACKING_ARGS):
        self.containers += [[to_add, args]]

    def go_to_parent(self) -> "Page":
        print("Switching from %s to %s." % (self.name, self.parent.name))
        self.turn_off()
        self.parent.turn_on()
        return self.parent
    def go_to_child(self, child_name) -> "Page":
        index = self.find_child(child_name)
        print("Switching from %s to %s." % (self.name, self.children[index].name))
        self.turn_off()
        self.children[index].turn_on()
        return self.children[index]

    def turn_on(self):
        print("Page %s turned on." % self.name)
        self.frame.pack()
        for container in self.containers:
            container[0].pack(**container[1])
            print("Container %s packed" % container)
    def turn_off(self):
        print("Page %s turned off." % self.name)
        self.frame.pack_forget()
        for container in self.containers:
            container[0].pack_forget()

    def find_child(self, child_name):
        for i in range(0, len(self.children)):
            if self.children[i] is None:
                continue
            if child_name == self.children[i].name:
                return i

        print("ERR: Child \"%s\" not found" % child_name)
        return -1

def switch_pages(current_page, child_name=""):
    current_page.go_to_child(child_name)

H3 = {"font":("Arial", 8, "bold"), "padx":10, "pady":5}

window = tk.Tk()
h = Page("Head Page", window)
c1 = Page("Child 1", window, h)
c2 = Page("Child 2", window, h)
c1_1 = Page("Child 1's child", window, c1)

h.add_child(c1)
h.add_child(c2)
c1.add_child(c1_1)

print(h)

h_lbl1 = tk.Label(h.frame, text="THIS IS A TEST", **H3)
h.add_containter(h_lbl1)

h_btn1 = tk.Button(h.frame, **H3, command=partial(switch_pages, h, "Child 1"))
h.add_containter(h_btn1)

c1_btn1 = tk.Button(c1.frame, **H3, command=partial(switch_pages, c1, "Child 1's child"))
c1.add_containter(c1_btn1)

h.turn_on()
window.mainloop()