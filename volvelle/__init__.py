# first, render the input A B C
# A -> A1, B -> B2, C -> C3
from browser import document, svg
from browser.html import SVG
preview = document.select_one(".preview")

def renderTable(rows):
    container = SVG(viewBox="-1 -1 2 2")
    container <= svg.circle(cx=0, cy=0, r=1, fill="white",
                            stroke="red", stroke_width=0.01)

    def renderRow(row):
        ret = svg.g()
        for idx, column in enumerate(row):
            ret <= svg.text(row[column], x=0, y=idx*0.1, font_size=0.1)
        return ret

    for row in rows:
        container <= renderRow(row)

    # TODO: clear preview
    preview.innerHTML = ""
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

        for inp in inputs:
            inpObj = getattr(self, inp)

            rows = []
            for inpOption in inpObj.options:
                row = {}
                row[inp] = inpOption
                for outp in outputs:
                    outpObj = getattr(self, outp)

                    inpObj.currentOption = inpOption
                    row[outp] = outpObj()
                    inpObj.currentOption = None

                rows.append(row)

            # Generate PostScript
            renderTable(rows)

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

