

class Args:
    def to_dict(self):
        return {"widget": "null"}


class Union(Args):
    def __init__(self, *args):
        self.args = args

    def to_dict(self):
        return {
            "widget": "choice",
            "args": [a.to_dict() for a in self.args]
        }


class Struct(Args):
    def __init__(self, *args):
        self.args = args

    def to_dict(self):
        return {
            "widget": "struct",
            "args": [a.to_dict() for a in self.args]
        }


class Array(Args):
    def __init__(self, element_type):
        self.type = element_type

    def to_dict(self):
        return {
            "widget": "array",
            "args": self.type.to_dict()
        }


class String(Args):
    def to_dict(self):
        return {
            "widget": "input"
        }


class Integer(Args):
    def __init__(self, min=0, max=100, type=None):
        self.min = min
        self.max = max
        self.type = type

    def to_dict(self):
        return {
            "widget": "integer",
            "args": {
                "min": self.min,
                "max": self.max,
                "type": self.type
            }
        }


class Spice(Integer):
    def __init__(self):
        super(Spice, self).__init__(min=0, type="spice")


class Constant(Args):
    def __init__(self, constant):
        self.constant = constant

    def to_dict(self):
        return {
            "widget": "constant",
            "args": self.constant
        }


class TraitorLeader(String):
    def to_dict(self):
        return {
            "widget": "traitor-select",
        }


class Leader(String):
    def to_dict(self):
        return {
            "widget": "leader-input"
        }


class Units(Args):
    def __init__(self, faction=None):
        self.fedaykin = faction == "fremen"
        self.sardaukar = faction == "emperor"

    def to_dict(self):
        return {
            "widget": "units",
            "args": {
                "fedaykin": self.fedaykin,
                "sardaukar": self.sardaukar
            }
        }


class RevivalUnits(Args):
    def __init__(self, units, max_units=3, single_2=True, title=None):
        self.units = units
        self.max_units = max_units
        self.single_2 = single_2
        self.title = title

    def to_dict(self):
        return {
            "widget": "revival-units",
            "args": {
                "units": self.units,
                "title": self.title,
                "maxUnits": self.max_units,
                "single2": self.single_2,
            }
        }


class RevivalLeader(Args):
    def __init__(self, leaders, required=False):
        self.leaders = leaders
        self.required = required

    def to_dict(self):
        return {
            "widget": "revival-leader",
            "args": {
                "leaders": self.leaders,
                "required": self.required,
            }
        }


class Space(String):
    def to_dict(self):
        return {
            "widget": "space-select"
        }


class Sector(Integer):
    def to_dict(self):
        return {
            "widget": "sector-select"
        }


class SpaceSector(Args):
    def to_dict(self):
        return {
            "widget": "space-sector-select-start",
            "args": {}
        }


class SpaceSectorStart(Args):
    def to_dict(self):
        return {
            "widget": "space-sector-select-start",
            "args": {}
        }


class SpaceSectorEnd(Args):
    def to_dict(self):
        return {
            "widget": "space-sector-select-end",
            "args": {}
        }


class FremenPlacementSelector(Args):
    def to_dict(self):
        return {
            "widget": "fremen-placement-select"
        }


class Battle(Args):
    def to_dict(self):
        return {
            "widget": "battle-select"
        }


class BattlePlan(Args):
    def __init__(self, faction, max_power):
        self.faction = faction
        self.max_power = max_power

    def to_dict(self):
        return {
            "widget": "battle-plan",
            "args": {
                "faction": self.faction,
                "max_power": self.max_power
            }
        }


class Faction(String):
    def to_dict(self):
        return {
            "widget": "faction-select"
        }


class MultiFaction(String):
    def __init__(self, factions):
        self.factions = factions

    def to_dict(self):
        return {
            "widget": "multi-faction-select",
            "args": {
                "factions": list(self.factions)
            }
        }


class Prescience(Args):
    def to_dict(self):
        return {
            "widget": "prescience"
        }


class PrescienceAnswer(Args):
    def __init__(self, max_power):
        self.max_power = max_power

    def to_dict(self):
        return {
            "widget": "prescience-answer",
            "args": {
                "max_power": self.max_power
            }
        }


class Voice(Args):
    def to_dict(self):
        return {
            "widget": "voice"
        }


class TankUnits(Args):
    def to_dict(self):
        return {
            "widget": "tank-units"
        }


class DiscardTreachery(Args):
    def to_dict(self):
        return {
            "widget": "discard-treachery"
        }


class ReturnTreachery(Args):
    def __init__(self, number):
        self.number = number

    def to_dict(self):
        return {
            "widget": "return-treachery",
            "args": {
                "number": self.number
            }
        }


class Turn(Integer):
    def __init__(self):
        super(Turn, self).__init__(min=0, max=10)


class Token(Integer):
    def to_dict(self):
        return {
            "widget": "token-select"
        }
