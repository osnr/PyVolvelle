# first, render the input A B C
# A -> A1, B -> B2, C -> C3
from browser import document, svg
from browser.html import SVG
preview = document.select_one(".preview")

def renderTable(table):
    container = SVG()
    for outp, tableForOutp in table.items():
        container <= svg.text("OK", x=70, y=25)

    # TODO: clear preview
    preview <= container

class Volvelle:
    def render(self):
        inputs = []
        outputs = []
        for propName in dir(self):
            if not propName.startswith("__") and propName != "render":
                prop = getattr(self, propName)
                if callable(prop):
                    outputs.append(propName)
                elif isinstance(prop, Input):
                    inputs.append(propName)

        for outp in outputs:
            getattr(self, outp)()

        table = {}
        for inp in inputs:
            inpObj = getattr(self, inp)
            if inp not in table:
                table[inp] = {}

            for outp in outputs:
                outpObj = getattr(self, outp)
                if outp not in table[inp]:
                    table[inp][outp] = {}

                # keep calling until entire input space has been
                # enumerated
                for inpOption in inpObj.options:
                    inpObj.currentOption = inpOption
                    table[inp][outp][inpOption] = outpObj()

            # Generate PostScript
            renderTable(table[inp])

class Input:
    pass
class OneOf(Input):
    def __init__(self):
        self.currentOption = None
        self.options = set()

    def __eq__(self, other):
        # instantiate other as an option; we'll run through the whole
        # table of input domain later
        if other not in self.options:
            self.options.add(other)
            return False

        return self.currentOption == other

