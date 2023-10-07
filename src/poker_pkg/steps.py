from collections import deque
from typing import List

from card_pkg.card_collection import CardCollection
from card_pkg.hand import Hand, PokerHand
from game_engine.engine import AbstractRoundStep
from game_engine.errors import EndOfStep

from .actions import (
    PokerActionName,
    PokerAllIn,
    PokerBet,
    PokerCall,
    PokerCheck,
    PokerFold,
    PokerRaise,
    PokerSwitchCards,
)
from .player import AbstractPokerPlayer
from .shuffler import AbstractShuffler, Shuffler


class PlayerStep(AbstractRoundStep):
    def start(self) -> None:
        self.game.all_players_played = False
        self.game.table.move_chip(0)
        self.game.current_player = self.game.table.get_nth_player(2).player

    def end(self) -> None:
        if self.maybe_end():
            self.game.current_player = None
            self.game.end_step()
            raise EndOfStep()

        self.game.next_player()

    def _get_players_left_to_talk(self) -> List[AbstractPokerPlayer]:
        return [
            s.player
            for s in self.game.table
            if self.game.pot.player_owed(s.player) != 0 and s.player.purse != 0
        ]

    def maybe_end(self) -> bool:
        if len(self.game.table) == 1:
            return True

        players_left = self._get_players_left_to_talk()

        if self.game.all_players_played and not len(players_left):
            return True

        return False


class BettingStep(PlayerStep):
    _action_map: dict = {
        PokerActionName.ALLIN: PokerAllIn,
        PokerActionName.BET: PokerBet,
        PokerActionName.CALL: PokerCall,
        PokerActionName.CHECK: PokerCheck,
        PokerActionName.FOLD: PokerFold,
        PokerActionName.RAISE: PokerRaise,
    }

    def _set_config(self, blinds_factory=None, **config) -> None:
        self.blinds_factory = (
            blinds_factory(self.game) if blinds_factory else None
        )


class BlindBettingStep(BettingStep):
    _action_map: dict = {
        PokerActionName.ALLIN: PokerAllIn,
        PokerActionName.BET: PokerBet,
        PokerActionName.CALL: PokerCall,
        PokerActionName.CHECK: PokerCheck,
        PokerActionName.FOLD: PokerFold,
        PokerActionName.RAISE: PokerRaise,
    }

    def start(self) -> None:
        super().start()

        if self.game_has_blinds:
            if len(self.game.players) == 2:
                self.game.current_player = self.game.table.get_nth_player(
                    1
                ).player

            self.game.bet(
                self.game.current_player,
                self.game.betting_structure.small_blind,
            )
            self.game.bet(
                self.game.current_player, self.game.betting_structure.big_blind
            )

    @property
    def game_has_blinds(self) -> bool:
        return (
            self.game.betting_structure.small_blind
            or self.game.betting_structure.big_blind
        )

    def _get_players_left_to_talk(self) -> List[AbstractPokerPlayer]:
        players = super()._get_players_left_to_talk()
        if players or not self.game_has_blinds:
            return players

        big_blind_player = self.game.table.get_nth_seat(3).player
        bbp_bets = self.game.pot.bets[big_blind_player]
        if self.game.current_player != big_blind_player and len(bbp_bets) < 2:
            return [self.game.table.get_nth_player(2).player]

        return []


class SwitchingStep(PlayerStep):
    _action_map = {
        PokerActionName.SWITCH: PokerSwitchCards,
    }


class StartRoundStep(PlayerStep):
    def _set_config(self, hand_factory: Hand = PokerHand, **config) -> None:
        self.hand_factory = hand_factory

    def start(self) -> None:
        self.game.table.activate_all()
        self.init_hands(self.game.table.players)
        self.game.end_step()

    def end(self) -> None:
        pass

    def maybe_end(self) -> None:
        pass

    def init_hands(self, players: list[AbstractPokerPlayer]) -> None:
        for p in players:
            p.hand = self.hand_factory()


class EndRoundStep(PlayerStep):
    def start(self) -> None:
        self._distribute_pot()
        self.game.end_step()

    def end(self) -> None:
        pass

    def maybe_end(self) -> None:
        pass

    def _distribute_pot(self) -> None:
        winners = self._find_winnners([s.player for s in self.game.table])
        self.game.pot.distribute(winners)

    # This is super weird... figure out why and fix
    def _find_winnners(
        self, players: List[AbstractPokerPlayer]
    ) -> List[List[AbstractPokerPlayer]]:
        winners = [[players[0]]]

        for p2 in players[1:]:
            inserted = False
            for i, w in enumerate(winners):
                if p2.hand > w[0].hand:
                    inserted = True
                    winners.insert(i, [p2])
                    break

                if p2.hand == w[0].hand:
                    inserted = True
                    w.append(p2)
                    break

            if not inserted:
                winners.append([p2])

        return winners


class DealStep(AbstractRoundStep):
    def _set_config(
        self, shuffler: AbstractShuffler = None, count: int = 5, **config
    ) -> None:
        self.shuffler = shuffler or Shuffler()
        self.count = count

    def start(self) -> None:
        self.game.dealer.shuffle()
        seats = deque(
            self.game.table._get_ordered_players(self.game.table._dealer_seat)
        )  # TODO: This is private!
        seats.rotate(-1)

        self._deal([s.player.hand for s in seats], count=self.count)
        self.game.end_step()

    def end(self) -> None:
        pass

    def maybe_end(self) -> None:
        pass

    def _deal(self, targets: List[CardCollection], count: int) -> None:
        self.game.dealer.deal(targets, count)


class CommunityCardStep(DealStep):
    def _set_config(
        self, cards_to_burn: int = 0, cards_to_reveal: int = 0, **config
    ) -> None:
        self.cards_to_burn = cards_to_burn
        self.cards_to_reveal = cards_to_reveal

    def start(self) -> None:
        self._deal([self.game._discard_pile], count=self.cards_to_burn)
        self._deal([self.game._community_pile], count=self.cards_to_reveal)
        self.game.end_step()
