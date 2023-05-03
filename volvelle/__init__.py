class Volvelle:
    def render(self):
        # trampoline that keeps calling compute until all combinations
        # have been enumerated
        inputs = []
        outputs = []
        for prop in dir(self):
            if not prop.startswith("__") and prop != "render":
                if callable(getattr(self, prop)):
                    outputs.append(prop)
                elif isinstance(prop, Input):
                    inputs.append(prop)

        table = {}
        for output in outputs:
            table[output] = {output: 3}
            getattr(self, output)()
        print(table)

class Input:
    pass
class OneOf(Input):
    def __init__(self):
        self.options = set()

    def __eq__(self, other):
        # instantiate other as an option; we'll run through the whole
        # table of input domain later
        if other not in self.options:
            self.options.add(other)
            return False

