from copy import deepcopy
from logging import getLogger

from dune.actions.action import Action
from dune.actions import args
from dune.exceptions import IllegalAction, BadCommand
from dune.actions.karama import discard_karama

logger = getLogger(__name__)


class Voice(Action):
    name = "voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "voice"
    ck_faction = "bene-gesserit"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 2:
            no, voice = parts
            if no != "no":
                raise BadCommand("No means no")
            no = True
        elif len(parts) == 1:
            voice = parts[0]
            no = False
        else:
            raise BadCommand("Bad args")

        if (voice not in [f"{flavor}-{category}"
                          for flavor in ["projectile", "poison"]
                          for category in ["weapon", "defense"]]) and (
            voice not in ("lasgun", "worthless", "cheap-hero-heroine")):
            raise BadCommand("Not something you can voice!")

        return Voice(faction, no, voice)

    @classmethod
    def get_arg_spec(clas, faction=None, game_state=None):
        return args.Voice()

    @classmethod
    def _check(cls, game_state, faction):
        if "bene-gesserit" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["bene-gesserit"]:
                if defender not in game_state.alliances["bene-gesserit"]:
                    raise IllegalAction("No legal voice is possible")

    def __init__(self, faction, no, voice):
        self.faction = faction
        self.no = no
        self.voice = voice

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        if self.faction == battle_id[0] or self.faction in new_game_state.alliances[battle_id[0]]:
            new_game_state.round_state.stage_state.voice_is_attacker = False
        elif self.faction == battle_id[1] or self.faction in new_game_state.alliances[battle_id[1]]:
            new_game_state.round_state.stage_state.voice_is_attacker = True
        else:
            raise BadCommand("You ain't voicing no one")

        new_game_state.round_state.stage_state.voice = (self.no, self.voice)
        new_game_state.round_state.stage_state.substage = "karama-voice"
        return new_game_state


class PassVoice(Action):
    name = "pass-voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "voice"
    ck_faction = "bene-gesserit"

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-sardaukar"
        return new_game_state


class SkipVoice(Action):
    name = "skip-voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "voice"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "bene-gesserit" in game_state.faction_state:
            if "bene-gesserit" in game_state.round_state.stage_state.battle:
                raise IllegalAction("The bene-gesserit may use the voice")
            if "bene-gesserit" in game_state.alliances[game_state.round_state.stage_state.battle[0]]:
                raise IllegalAction("The bene-gesserit may use the voice on behalf of their attacker ally")
            if "bene-gesserit" in game_state.alliances[game_state.round_state.stage_state.battle[1]]:
                raise IllegalAction("The bene-gesserit may use the voice on behalf of their defender ally")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-sardaukar"
        return new_game_state


class KaramaVoice(Action):
    name = "karama-voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-voice"
    ck_karama = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction in game_state.round_state.stage_state.voice_karama_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.voice_is_attacker = False
        new_game_state.round_state.stage_state.voice = None
        new_game_state.round_state.stage_state.substage = "karama-sardaukar"
        discard_karama(new_game_state, self.faction)
        return new_game_state


class KaramaPassVoice(Action):
    name = "karama-pass-voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-voice"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "bene-gesserit":
            raise IllegalAction("You cannot karam your own voice!")
        if faction in game_state.round_state.stage_state.voice_karama_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.voice_karama_passes.append(self.faction)
        return new_game_state


class SkipKaramaVoice(Action):
    name = "skip-karama-voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-voice"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.stage_state.voice_karama_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Still waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-sardaukar"
        return new_game_state
