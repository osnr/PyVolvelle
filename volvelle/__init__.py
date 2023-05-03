class Volvelle:
    def render(self):
        # trampoline that keeps calling each output until all
        # combinations have been enumerated
        inputs = []
        outputs = []
        for prop in dir(self):
            if not prop.startswith("__") and prop != "render":
                prop = getattr(self, prop)
                if callable(prop):
                    outputs.append(prop)
                elif isinstance(prop, Input):
                    inputs.append(prop)

        for outp in outputs:
            outp()

        for inp in inputs:
            table = {}
            for outp in outputs:
                for inpOption in inp.options:
                    inp.currentOption = inpOption
                    table[inpOption] = outp()

            print(inp, table)

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

