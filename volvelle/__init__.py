import sys

from browser import document, svg, console, window
from browser.html import SVG
preview = document.select_one(".preview")

class Volvelle:
    def render(self):
        inputs = []
        outputs = []
        for propName in dir(self):
            if not propName.startswith("__") and not hasattr(Volvelle, propName):
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
            self.renderTable(rows)

    def renderTable(self, rows):
        container = SVG(viewBox="-100 -100 200 200")
        # We need to mount the container so we can attach events to
        # the SVG subelements.
        preview.innerHTML = ""
        preview <= container
        container <= svg.circle(cx=0, cy=0, r=100, fill="white",
                                stroke="red", stroke_width=0.01)

        self.drag = None
        def handleMouseDown(column, ev):
            self.drag = {"target": ev.target, "column": column,
                         "startX": ev.pageX, "startY": ev.pageY}
            document.body.bind("mousemove", handleMouseMove)
            document.body.bind("mouseup", handleMouseUp)

        def handleMouseMove(ev):
            if not self.drag:
                return
            dx = ev.pageX - self.drag["startX"]
            dy = ev.pageY - self.drag["startY"]
            print("Dragging", self.drag["column"])
            print(window.code.split('\n')[getattr(self, self.drag["column"]).callerLineNumber - 1])

        def handleMouseUp(ev):
            self.drag = None
            document.body.unbind("mousemove", handleMouseMove)
            document.body.unbind("mouseup", handleMouseUp)

        def renderRow(row):
            ret = svg.g()
            for idx, column in enumerate(row):
                ret <= renderField(idx, column)
            return ret

        def renderField(idx, column):
            field = svg.text(row[column], x=0, y=idx*10, font_size=10)
            field.bind("mousedown", lambda ev: handleMouseDown(column, ev))
            return field

        for idx, row in enumerate(rows):
            rowG = renderRow(row)
            rowG.setAttribute("transform", "rotate(" + str(idx/len(rows) * 360) + ") translate(50)")
            container <= rowG


class Input:
    pass


class OneOf(Input):
    def __init__(self):
        self.callerLineNumber = sys._getframe(1).f_lineno

        self.currentOption = None
        self.options = {}

    def __eq__(self, other):
        # instantiate other as an option; we'll run through the whole
        # table of input domain later
        if other not in self.options:
            self.options[other] = True
            return False

        return self.currentOption == other
