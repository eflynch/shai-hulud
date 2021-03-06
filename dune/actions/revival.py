from copy import deepcopy

from dune.actions import storm, args
from dune.actions.common import get_faction_order, spend_spice
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.state.rounds.movement import MovementRound
from dune.state.leaders import parse_leader
from dune.actions.karama import discard_karama


def get_revivable_leaders(game_state, faction):
    fs = game_state.faction_state[faction]
    non_captured_leaders = [leader[0] for leader in fs.leaders[:] + fs.tank_leaders[:]]

    leader_death_count = game_state.faction_state[faction].leader_death_count

    def _ldc(leader_name):
        if leader_name in leader_death_count:
            return leader_death_count[leader_name]
        else:
            return 0

    min_count = min([_ldc(leader_name) for leader_name in non_captured_leaders])

    all_revivable_leaders = []

    if faction == "atreides":
        kwisatz_haderach_tanks = fs.kwisatz_haderach_tanks
        if kwisatz_haderach_tanks is not None and kwisatz_haderach_tanks <= min_count:
            all_revivable_leaders.append(("Kwisatz-Haderach", 2))

    for leader in fs.tank_leaders:
        if _ldc(leader[0]) <= min_count:
            all_revivable_leaders.append(leader)

    return all_revivable_leaders


class ProgressRevival(Action):
    name = "progress-revival"
    ck_round = "revival"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.faction_turn is not None:
            if get_revivable_leaders(game_state, game_state.round_state.faction_turn):
                raise IllegalAction("They might want to revive that leader")

            if game_state.faction_state[game_state.round_state.faction_turn].tank_units:
                raise IllegalAction("They might want to revive those units")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for faction in get_faction_order(game_state):
            if faction in game_state.round_state.factions_done:
                continue
            if game_state.faction_state[faction].tank_units:
                new_game_state.round_state.faction_turn = faction
                return new_game_state
            if get_revivable_leaders(game_state, faction):
                new_game_state.round_state.faction_turn = faction
                return new_game_state

        new_game_state.round_state = MovementRound()
        return new_game_state


def parse_revival_units(args):
    if not args:
        return []

    units = []
    for i in args.split(","):
        if i in ["1", "2"]:
            units.append(int(i))
        else:
            raise BadCommand("What sort of unit is _that_?")
    return units


def parse_revival_leader(args):
    if (args == "") or (args == "-"):
        return None
    if args == "Kwisatz-Haderach":
        return ("Kwisatz-Haderach", 2)
    else:
        return parse_leader(args)


def _get_leader_cost(leader):
    return leader[1] if leader else 0


def _get_unit_cost(faction, units, fremen_blessing=False):
    if fremen_blessing:
        return 0

    cost = len(units) * 2
    if faction in ["emperor", "bene-gesserit", "guild"]:
        cost = max(0, cost - 2)
    if faction in ["atreides", "harkonnen"]:
        cost = max(0, cost - 4)
    if faction == "fremen":
        cost = 0
    return cost


def revive_units(units, faction, game_state):
    for u in units:
        if u not in game_state.faction_state[faction].tank_units:
            raise BadCommand("Those units are not in the tanks")
        game_state.faction_state[faction].tank_units.remove(u)
        game_state.faction_state[faction].reserve_units.append(u)


def revive_leader(leader, faction, game_state):
    if leader is not None:
        if leader[0] == "Kwisatz-Haderach":
            if game_state.faction_state[faction].kwisatz_haderach_tanks is None:
                raise BadCommand("There's no kwisatz haderach to revive!")
            game_state.faction_state[faction].kwisatz_haderach_tanks = None
        else:
            if leader not in game_state.faction_state[faction].tank_leaders:
                raise BadCommand("You can't revive that leader, because they are not in the tanks!")
            game_state.faction_state[faction].tank_leaders.remove(leader)
            game_state.faction_state[faction].leaders.append(leader)


def _execute_revival(units, leader, faction, game_state, cost):
    new_game_state = deepcopy(game_state)
    spend_spice(new_game_state, faction, cost)
    revive_units(units, faction, new_game_state)
    revive_leader(leader, faction, new_game_state)

    return new_game_state


class KaramaFreeUnitRevival(Action):
    name = "karama-free-unit-revival"
    ck_karama = True
    ck_faction_karama = "emperor"

    def __init__(self, faction, units):
        self.faction = faction
        self.units = units

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.faction_state[faction].tank_units:
            raise IllegalAction("You don't have any units to revive")

    @classmethod
    def parse_args(cls, faction, args):
        units = parse_revival_units(args)
        if not units:
            raise IllegalAction("Can't revive no units")
        return KaramaFreeUnitRevival(faction, units)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.RevivalUnits(game_state.faction_state[faction].tank_units,
                                 single_2=False)

    def _execute(self, game_state):
        if len(self.units) > 3:
            raise BadCommand("You can only revive up to three units")
        new_game_state = deepcopy(game_state)
        revive_units(self.units, self.faction, new_game_state)
        discard_karama(new_game_state, self.faction)
        new_game_state.faction_state[self.faction].used_faction_karama = True
        return new_game_state


class KaramaFreeLeaderRevival(Action):
    name = "karama-free-leader-revival"
    ck_karama = True
    ck_faction_karama = "emperor"

    def __init__(self, faction, leader):
        self.faction = faction
        self.leader = leader

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.faction_state[faction].tank_leaders:
            raise IllegalAction("You don't have any leaders to revive")

    @classmethod
    def parse_args(cls, faction, args):
        leader = parse_revival_leader(args)
        if leader is None:
            raise BadCommand("Can't revive not a leader for free!")
        return KaramaFreeLeaderRevival(faction, leader)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.RevivalLeader(game_state.faction_state[faction].tank_leaders,
                                  required=True)

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        revive_leader(self.leader, self.faction, new_game_state)
        discard_karama(new_game_state, self.faction)
        new_game_state.faction_state[self.faction].used_faction_karama = True
        return new_game_state


class FremenBlessing(Action):
    name = "allow-free-ally-revival"
    ck_round = "revival"
    ck_faction = "fremen"

    @classmethod
    def parse_args(cls, faction, args):
        allies = args.split(" ")
        return FremenBlessing(faction, allies)

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.alliances[faction]:
            raise IllegalAction("You cannot give allies free revival if you have no allies")

    def __init__(self, faction, allies):
        self.faction = faction
        self.allies = allies

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        factions = game_state.alliances[faction]
        return args.MultiFaction(factions=factions)

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.fremen_blessings = []
        for ally in self.allies:
            if ally not in new_game_state.alliances[self.faction]:
                raise BadCommand("You cannot give free revival to non-allies")
            new_game_state.round_state.fremen_blessings.append(ally)
        return new_game_state


class EmperorAllyRevival(Action):
    name = "revive-ally-units"
    ck_round = "revival"
    ck_faction = "emperor"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ") if args != "" else []
        if len(parts) % 2 != 0:
            raise BadCommand("Need to specify units and faction per ally")

        revivals = {}
        for i in range(0, len(parts), 2):
            ally = parts[i]
            units = parts[i+1]
            units = parse_revival_units(units)
            revivals[ally] = units

        return EmperorAllyRevival(faction, revivals)

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.alliances[faction]:
            raise IllegalAction("You cannot give allies free revivals if you have no allies")
        if game_state.round_state.emperor_ally_revival_done:
            raise IllegalAction("You already did your special revival")

    def __init__(self, faction, revivals):
        self.faction = faction
        self.revivals = revivals

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        revivals = []
        for f in game_state.alliances[faction]:
            revivals.append(args.RevivalUnits(
                game_state.faction_state[faction].tank_units,
                max_units=3,
                single_2=False,
                title=f))
        return args.Struct(*revivals)

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.emperor_ally_revival_done = True
        for ally in self.revivals:
            if ally not in new_game_state.alliances[self.faction]:
                raise BadCommand("You cannot give free revival to non-allies")
            units = self.revivals[ally]
            if len(units) > 3:
                raise BadComand("You can only revive 3 units for your allies")

            cost = 2 * len(units)
            spend_spice(new_game_state, self.faction, cost)
            revive_units(units, ally, new_game_state)
        new_game_state.round_state.emperor_ally_revival_done = True
        return new_game_state


class Revive(Action):
    name = "revive"
    ck_round = "revival"

    @classmethod
    def parse_args(cls, faction, args):
        if not args:
            return Revive(faction, [], None)
        units, leader = args.split(" ")
        return Revive(faction, parse_revival_units(units), parse_revival_leader(leader))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(
            args.RevivalUnits(game_state.faction_state[faction].tank_units),
            args.RevivalLeader(get_revivable_leaders(game_state, faction))
        )

    def __init__(self, faction, units, leader):
        self.faction = faction
        self.units = units
        self.leader = leader

    @classmethod
    def _check(cls, game_state, faction):
        if (not game_state.faction_state[faction].tank_units) and \
           get_revivable_leaders(game_state, faction):
            raise IllegalAction("You don't have anything to revive")
        Action.check_turn(game_state, faction)

    def _execute(self, game_state):
        if self.leader and self.leader not in get_revivable_leaders(game_state, self.faction):
            raise BadCommand("That leader is not revivable")
        if len(self.units) > 3:
            raise BadCommand("You can only revive up to three units")
        if self.units.count("2") > 1:
            raise BadCommand("Only 1 Sardukar or Fedykin can be be revived per turn")

        has_fremen_blessing = self.faction in game_state.round_state.fremen_blessings
        cost = _get_unit_cost(self.faction, self.units, has_fremen_blessing) + _get_leader_cost(self.leader)
        new_game_state = _execute_revival(self.units, self.leader, self.faction, game_state, cost)
        faction_order = get_faction_order(game_state)
        index = faction_order.index(self.faction) + 1
        if index < len(faction_order):
            new_game_state.round_state.factions_done.append(self.faction)
            new_game_state.round_state.faction_turn = faction_order[index]
        else:
            new_game_state.round_state = MovementRound()
        return new_game_state
