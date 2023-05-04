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
                    prop.name = propName
                    inputs.append(propName)

        for outp in outputs:
            getattr(self, outp)()

        container = SVG(viewBox="-100 -100 200 200")
        # We need to mount the container so we can attach events to
        # the SVG subelements.
        preview.innerHTML = ""
        preview <= container
        container <= svg.circle(cx=0, cy=0, r=100, fill="white",
                                stroke="red", stroke_width=0.01)

        for inp in inputs:
            inpObj = getattr(self, inp)
            inpObj.render(self, container, outputs)


class Input:
    pass


class Slide(Input):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __mul__(self, other):
        return Slide(self.a * other, self.b * other)

    def render(self, volvelle, container, outputs, sep=0):
        container <= svg.circle(cx=0, cy=0, r=80-sep, fill="none",
                                stroke="black", stroke_width=1)
        for i in range(self.a, self.b):
            label = svg.text(i, x=0, y=-80+sep)
            label.setAttribute("transform", "rotate(" + str((i - self.a)/(self.b - self.a) * 360) + ")")
            container <= label

        for outp in outputs:
            outpObj = getattr(volvelle, outp)
            outpSlide = outpObj()

            outpSlide.render(volvelle, container, [], sep=sep+20)

class OneOf(Input):
    def __init__(self, sep=10):
        self.callerLineNumber = sys._getframe(1).f_lineno

        self.sep = sep

        self.currentChoice = None
        self.choices = {}

    def __eq__(self, other):
        # Remember that `other` is a possible choice; the renderer
        # will run through the whole table of possible choices in
        # another pass later.
        if other not in self.choices:
            self.choices[other] = True
            return False

        return self.currentChoice == other

    def render(self, volvelle, container, outputs):
        rows = []
        for choice in self.choices:
            row = {}
            row[self.name] = choice
            for outp in outputs:
                outpObj = getattr(volvelle, outp)

                self.currentChoice = choice
                row[outp] = outpObj()
                self.currentChoice = None

            rows.append(row)

        # Generate PostScript:
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
            column = getattr(volvelle, columnName)
            sep = column.sep if hasattr(column, "sep") else 10
            field = svg.text(row[columnName], x=0, y=sep+(idx*sep), font_size=10)
            field.bind("mousedown", lambda ev: handleMouseDown(column, ev))
            return field

        for idx, row in enumerate(rows):
            rowG = renderRow(row)
            rowG.setAttribute("transform", "rotate(" + str(idx/len(rows) * 360) + ") translate(50)")
            container <= rowG
