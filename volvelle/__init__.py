import sys
import re
import math
import types

from browser import document, svg, console, window
from browser.html import SVG
preview = document.select_one(".preview")

class Volvelle(object):
    def render(self):
        self._inputs = {}
        self._outputs = {}
        for propName in dir(self):
            if not propName.startswith("_") and not hasattr(Volvelle, propName):
                prop = getattr(self, propName)
                if isinstance(prop, Output):
                    self._outputs[propName] = prop
                elif callable(prop):
                    prop = Output(prop, name=propName)
                    self._outputs[propName] = prop
                elif isinstance(prop, Input):
                    prop.name = propName
                    self._inputs[propName] = prop

        for outp in self._outputs.values():
            outp.fn()

        dataContainer = SVG(viewBox="-110 -110 220 220")
        selectorContainer = SVG(viewBox="-110 -110 220 220")
        # We need to mount the container so we can attach events to
        # the SVG subelements.
        preview.innerHTML = ""
        preview <= dataContainer
        preview <= selectorContainer

        dataContainer.innerHTML = selectorContainer.innerHTML = """
<defs>
    <clipPath id="clip-volvelle">
      <circle cx="0" cy="0" r="100" />
    </clipPath>
</defs>
        """
        dataContainer <= svg.circle(id="volvelle-data",
                                    cx=0, cy=0, r=100, fill="white",
                                    stroke="#555", stroke_width=0.5)
        dataG = svg.g()
        dataContainer <= dataG
        dataG.setAttribute("clip-path", "url(#clip-volvelle)")

        selectorContainer <= svg.circle(id="volvelle-selector",
                                        cx=0, cy=0, r=100, fill="white",
                                        stroke="#555", stroke_width=0.5)
        selectorG = svg.g()
        selectorContainer <= selectorG
        selectorG.setAttribute("clip-path", "url(#clip-volvelle)")

        for inp in self._inputs.values():
            inp.render(dataG, selectorG, self._inputs, self._outputs)


class Input:
    pass


class Slide(Input):
    def __init__(self, a, b, offsetAngle=0, offsetDistance=0):
        self.a = a
        self.b = b

        self.offsetAngle = offsetAngle
        self.offsetDistance = offsetDistance

    def __mul__(self, other):
        return Slide(self.a * other, self.b * other)

    def __add__(self, other):
        return Slide(self.a + other, self.b + other)

    def render(self, dataContainer, selectorContainer,
               inputs, outputs, sep=0):
        dataContainer <= svg.circle(cx=0, cy=0, r=80-sep, fill="none",
                                    stroke="black", stroke_width=1)
        for i in range(self.a, self.b):
            label = svg.text(i, x=0, y=-80+sep)
            label.setAttribute("transform", "rotate(" + str((i - self.a)/(self.b - self.a) * 360) + ")")
            dataContainer <= label

        for outp in outputs.values():
            outpSlide = outp.fn()

            outpSlide.render(dataContainer, [], [], sep=sep+20)

class OneOf(Input):
    def __init__(self, offsetAngle=0, offsetDistance=0):
        self.callerLineNumber = sys._getframe(1).f_lineno

        self.offsetAngle = offsetAngle
        self.offsetDistance = offsetDistance

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

    def render(self, dataContainer, selectorContainer,
               inputs, outputs):
        rows = []
        for choice in self.choices:
            row = {}
            row[self.name] = choice
            for outp in outputs.values():
                self.currentChoice = choice
                row[outp.name] = outp.fn()
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
            dr = math.sqrt(dx**2 + dy**2)
            dtheta = math.atan2(dy, dx)

            lines = window.code.split('\n')
            line = lines[self.drag["column"].callerLineNumber-1]
            if line.lstrip().startswith("def "): # it's an output
                prevline = lines[self.drag["column"].callerLineNumber-2]
                if prevline.lstrip().startswith("@output"):
                    prevline = prevline.replace("@output()", "@output(offsetDistance=0, offsetAngle=0)")
                    prevline = re.sub(r"offsetDistance=[\-\d\.]+", f"offsetDistance={dr:.4f}", prevline)
                    prevline = re.sub(r"offsetAngle=[\-\d\.]+", f"offsetAngle={dtheta:.4f}", prevline)
                    start = len("\n".join(lines[0:self.drag["column"].callerLineNumber-2])) + 1
                    end = start + len(lines[self.drag["column"].callerLineNumber-2])
                    window.replaceLine(start, end, prevline)
                else:
                    start = len("\n".join(lines[0:self.drag["column"].callerLineNumber-1])) + 1
                    window.replaceLine(start, start, re.match(r"[ \t]+", line)[0] + "@output(offsetDistance=0, offsetAngle=0)\n")
            else:
                start = len("\n".join(lines[0:self.drag["column"].callerLineNumber-1])) + 1
                end = start + len(line)
                line = line.replace("OneOf()", "OneOf(offsetDistance=0, offsetAngle=0)")
                line = re.sub(r"offsetDistance=[\-\d\.]+",f"offsetDistance={dr:.4f}", line)
                line = re.sub(r"offsetAngle=[\-\d\.]+", f"offsetAngle={dtheta:.4f}", line)
                window.replaceLine(start, end, line)

        def handleMouseUp(ev):
            self.drag = None
            document.body.unbind("mousemove", handleMouseMove)
            document.body.unbind("mouseup", handleMouseUp)

        def renderRow(row, boxesOnly=False):
            ret = svg.g()
            for columnIdx, columnName in enumerate(row):
                ret <= renderField(columnIdx, row, columnName, boxesOnly)
            return ret

        def renderField(columnIdx, row, columnName, boxesOnly=False):
            column = outputs[columnName] if columnName in outputs else inputs[columnName]
            offsetDistance = column.offsetDistance if hasattr(column, "offsetDistance") else columnIdx*20
            offsetAngle = column.offsetAngle if hasattr(column, "offsetAngle") else 0
            if boxesOnly:
                field = svg.g()
                field <= svg.rect(x=offsetDistance*math.cos(offsetAngle),
                                  y=offsetDistance*math.sin(offsetAngle),
                                  width=40,
                                  height=10,
                                  stroke="#999", stroke_width=1,
                                  fill="white")
                field <= svg.text(columnName,
                                  x=offsetDistance*math.cos(offsetAngle),
                                  y=offsetDistance*math.sin(offsetAngle) - 1,
                                  font_size=10,
                                  fill="#999")
            else:
                field = svg.text(row[columnName],
                                 x=offsetDistance*math.cos(offsetAngle),
                                 y=offsetDistance*math.sin(offsetAngle),
                                 font_size=10)
            field.style.cursor = "move"
            field.bind("mousedown", lambda ev: handleMouseDown(column, ev))
            return field

        for idx, row in enumerate(rows):
            rowG = renderRow(row)
            rowG.setAttribute("transform", "rotate(" + str(idx/len(rows) * 360) + ") translate(50)")
            dataContainer <= rowG

            if idx == 0:
                selectorRowG = renderRow(row, boxesOnly=True)
                selectorRowG.setAttribute("transform", "rotate(" + str(idx/len(rows) * 360) + ") translate(50)")
                selectorContainer <= selectorRowG


class Output:
    def __init__(self, fn, name, offsetDistance=0, offsetAngle=0):
        self.fn = fn
        self.name = name
        self.callerLineNumber = fn.__code__.co_firstlineno

        self.offsetDistance = offsetDistance
        self.offsetAngle = offsetAngle

    def __get__(self, instance, owner):
        self.fn = types.MethodType(self.fn, instance)
        return self


def output(offsetDistance=0, offsetAngle=0):
    def decorator(fn):
        return Output(fn=fn, name=fn.__name__,
                      offsetDistance=offsetDistance, offsetAngle=offsetAngle)

    return decorator
