class Step(object):
    """ A Step in the world generation process.
        The process starts with plates simulation and go on through different
        intermediate steps to reach the 'full' step.
    """

    def __init__(self, name):
        self.name = name
        self.include_plates = True
        self.include_precipitations = False
        self.include_erosion = False
        self.include_biome = False

    @staticmethod
    def get_by_name(name):
        if name == "plates":
            return Step.plates()
        elif name == "precipitations":
            return Step.precipitations()
        elif name == "full":
            return Step.full()
        raise Exception("Unknown step '%s'" % name)

    @classmethod
    def full(cls):
        if not hasattr(cls, "_full"):
            step = Step("full")
            step.include_precipitations = True
            step.include_erosion = True
            step.include_biome = True
            cls._full = step
        return cls._full

    @classmethod
    def precipitations(cls):
        if not hasattr(cls, "_precipitations"):
            step = Step("precipitations")
            step.include_precipitations = True
            cls._precipitations = step
        return cls._precipitations

    @classmethod
    def plates(cls):
        if not hasattr(cls, "_plates"):
            step = Step("plates")
            step.include_precipitations = True
            step.include_erosion = True
            step.include_biome = True
            cls._plates = step
        return cls._plates

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.__dict__ == other.__dict__
