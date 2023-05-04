import sys
import re

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
            print("Dragging", dy, self.drag["column"])

            lines = window.code.split('\n')
            line = lines[self.drag["column"].callerLineNumber-1]
            start = len("\n".join(lines[0:self.drag["column"].callerLineNumber-1])) + 1
            end = start + len(line)
            line = line.replace("OneOf()", "OneOf(sep=10)")
            line = re.sub(r"sep=[\-\d]+", "sep=" + str(dy), line)
            window.replaceLine(start, end, line)

        def handleMouseUp(ev):
            self.drag = None
            document.body.unbind("mousemove", handleMouseMove)
            document.body.unbind("mouseup", handleMouseUp)

        def renderRow(row):
            ret = svg.g()
            for idx, columnName in enumerate(row):
                ret <= renderField(idx, row, columnName)
            return ret

        def renderField(idx, row, columnName):
            column = getattr(self, columnName)
            sep = column.sep if hasattr(column, "sep") else 10
            field = svg.text(row[columnName], x=0, y=sep+(idx*sep), font_size=10)
            field.bind("mousedown", lambda ev: handleMouseDown(column, ev))
            return field

        for idx, row in enumerate(rows):
            rowG = renderRow(row)
            rowG.setAttribute("transform", "rotate(" + str(idx/len(rows) * 360) + ") translate(50)")
            container <= rowG


class Input:
    pass


class OneOf(Input):
    def __init__(self, sep=10):
        self.callerLineNumber = sys._getframe(1).f_lineno

        self.sep = sep

        self.currentOption = None
        self.options = {}

    def __eq__(self, other):
        # instantiate other as an option; we'll run through the whole
        # table of input domain later
        if other not in self.options:
            self.options[other] = True
            return False

        return self.currentOption == other
