from volvelle import *

class Doubler(Volvelle):
    def __init__(self):
        self.x = Slide(1, 10)

    def twox(self):
        return self.x * 2

Names().render()
