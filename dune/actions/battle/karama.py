from copy import deepcopy
from logging import getLogger

from dune.actions.action import Action
from dune.exceptions import IllegalAction
from dune.actions.karama import discard_karama

logger = getLogger(__name__)


class KaramaKwizatzHaderach(Action):
    name = "karama-kwizatz-haderach"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-kwizatz-haderach"
    ck_karama = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "atreides":
            raise IllegalAction("You cannot karama your own messiah")
        if "atreides" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No Kwizatz to Haderach")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_kwizatz_haderach = True
        new_game_state.round_state.stage_state.substage = "karama-sardaukar"
        discard_karama(game_state, self.faction)
        return new_game_state


class KaramaPassKwizatzHaderach(Action):
    name = "karama-pass-kwizatz-haderach"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-kwizatz-haderach"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "atreides":
            raise IllegalAction("You cannot karama your own messiah")
        if "atreides" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No Kwizatz to Haderach")
        if faction in game_state.round_state.stage_state.karama_kwizatz_haderach_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_kwizatz_haderach_passes.append(self.faction)
        return new_game_state


class SkipKaramaKwizatzHaderach(Action):
    name = "skip-karama-kwizatz-haderach"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-kwizatz-haderach"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" in game_state.faction_state:
            if "atreides" in game_state.round_state.stage_state.battle:
                passes = len(game_state.round_state.stage_state.karama_kwizatz_haderach_passes)
                if passes != len(game_state.faction_state) - 1:
                    raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-sardaukar"
        return new_game_state


class KaramaSardaukar(Action):
    name = "karama-sardaukar"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-sardaukar"
    ck_karama = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "emperor":
            raise IllegalAction("You cannot karama your own slave soldier things")
        if "emperor" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No sar to kar")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_sardaukar = True
        new_game_state.round_state.stage_state.substage = "karama-fedaykin"
        discard_karma(new_game_state, self.faction)
        return new_game_state


class KaramaPassSardaukar(Action):
    name = "karama-pass-sardaukar"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-sardaukar"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "emperor":
            raise IllegalAction("You cannot karama your own slave soldier things")
        if "emperor" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No sar to kar")
        if faction in game_state.round_state.stage_state.karama_sardaukar_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_sardaukar_passes.append(self.faction)
        return new_game_state


class SkipKaramaSardaukar(Action):
    name = "skip-karama-sardaukar"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-sardaukar"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "emperor" in game_state.faction_state:
            if "emperor" in game_state.round_state.stage_state.battle:
                if len(game_state.round_state.stage_state.karama_sardaukar_passes) != len(game_state.faction_state) - 1:
                    raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-fedaykin"
        return new_game_state


class KaramaFedaykin(Action):
    name = "karama-fedaykin"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-fedaykin"
    ck_karam = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "fremen":
            raise IllegalAction("You cannot karama your own man dudes")
        if "fremen" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No fedaykin")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_fedaykin = True
        new_game_state.round_state.stage_state.substage = "finalize"
        discard_karama(new_game_state, self.faction)
        return new_game_state


class KaramaPassFedaykin(Action):
    name = "karama-pass-fedaykin"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-fedaykin"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "fremen":
            raise IllegalAction("You cannot karama your own main dudes")
        if "fremen" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("no fedaykin")
        if faction in game_state.round_state.stage_state.karama_fedaykin_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_fedaykin_passes.append(self.faction)
        return new_game_state


class SkipKaramaFedaykin(Action):
    name = "skip-karama-fedaykin"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-fedaykin"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "fremen" in game_state.faction_state:
            if "fremen" in game_state.round_state.stage_state.battle:
                if len(game_state.round_state.stage_state.karama_fedaykin_passes) != len(game_state.faction_state) - 1:
                    raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "finalize"
        return new_game_state
