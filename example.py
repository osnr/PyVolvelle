from volvelle import *

class Ages(Volvelle):
    def __init__(self):
        self.person = OneOf()

    def age(self):
        if self.person == "Omar":
            return "Rizwan"
        elif self.person == "Max":
            return "Krieger"
        elif self.person == "Ian":
            return "Clester"
        elif self.person == "Andrew":
            return "Blinn"

Ages().render()
