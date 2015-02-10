__author__ = 'Federico Tomassetti'

class Step(object):
    def __init__(self, name):
        self.name = name
        self.include_plates = True
        self.include_precipitations = False
        self.include_erosion = False
        self.include_biome = False

    @staticmethod
    def get_by_name(name):
        step = None
        if name == "plates":
            step = Step(name)
        elif name == "precipitations":
            step = Step(name)
            step.include_precipitations = True
        elif name == "full":
            step = Step(name)
            step.include_precipitations = True
            step.include_erosion = True
            step.include_biome = True

        return step

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)