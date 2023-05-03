from volvelle import *

class Names(Volvelle):
    def __init__(self):
        self.firstname = OneOf()

    def lastname(self):
        if self.firstname == "Omar":
            return "Rizwan"
        elif self.firstname == "Max":
            return "Krieger"
        elif self.firstname == "Ian":
            return "Clester"
        elif self.firstname == "Andrew":
            return "Blinn"

Names().render()
