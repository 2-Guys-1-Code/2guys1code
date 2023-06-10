from typing import List

from card_pkg.card_collection import CardCollection
from card_pkg.hand import Hand, PokerHand
from game_engine.engine import AbstractAction, AbstractRoundStep
from game_engine.errors import EndOfStep, IllegalActionException

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
        self.game._table.current_player = self.game._table.get_nth_player(1)

    def end(self) -> None:
        self.game._table.current_player = None
        self.game.end_step()
        raise EndOfStep()

    # This should be "end", which raises if we cannot end
    def maybe_end(self) -> None:
        if len(self.game._table) == 1:
            self.end()

        players_left = [
            p for _, p in self.game._table if self.game.pot.player_owed(p) != 0 and p.purse != 0
        ]

        if self.game.all_players_played and not len(players_left):
            self.end()


class BettingStep(PlayerStep):
    _action_map: dict = {
        PokerActionName.ALLIN: PokerAllIn,
        PokerActionName.BET: PokerBet,
        PokerActionName.CALL: PokerCall,
        PokerActionName.CHECK: PokerCheck,
        PokerActionName.FOLD: PokerFold,
        PokerActionName.RAISE: PokerRaise,
    }


class SwitchingStep(PlayerStep):
    _action_map = {
        PokerActionName.SWITCH: PokerSwitchCards,
    }


class StartRoundStep(PlayerStep):
    def _set_config(self, hand_factory: Hand = PokerHand, **config) -> None:
        self.hand_factory = hand_factory

    def start(self) -> None:
        self.game._table.activate_all()
        self.init_hands(self.game._table.players)
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
        self._return_cards(
            [p.hand for p in self.game._table.seats.values() if p is not None]
            + [self.game._community_pile, self.game._discard_pile]
        )
        self._remove_broke_players()
        self.game.end_step()

    def end(self) -> None:
        pass

    def maybe_end(self) -> None:
        pass

    def _distribute_pot(self) -> None:
        winners = self._find_winnners([p for _, p in self.game._table])
        self.game.pot.distribute(winners)

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

    def _return_cards(self, collections: List[CardCollection]) -> None:
        for c in collections:
            # It would be nice to be able to pull all cards
            for i in range(len(c), 0, -1):
                card = c.pull_from_position(i)
                self.game._deck.insert_at_end(card)

    def _remove_broke_players(self):
        for _, p in self.game._table:
            if p.purse == 0:
                self.game._table.leave(p)


class DealStep(AbstractRoundStep):
    def _set_config(self, shuffler: AbstractShuffler = None, count: int = 5, **config) -> None:
        self.shuffler = shuffler or Shuffler()
        self.count = count

    def start(self) -> None:
        self._shuffle(self.game._deck)
        self._deal([p.hand for _, p in self.game._table], count=self.count)
        self.game.end_step()

    def end(self) -> None:
        pass

    def maybe_end(self) -> None:
        pass

    def _shuffle(self, deck: CardCollection) -> None:
        self.shuffler.shuffle(deck)

    def _deal(self, targets: List[CardCollection], count: int) -> None:
        for _ in range(0, count):
            for t in targets:
                t.insert_at_end(self.game._deck.pull_from_top())


class CommunityCardStep(DealStep):
    def _set_config(self, cards_to_burn: int = 0, cards_to_reveal: int = 0, **config) -> None:
        self.cards_to_burn = cards_to_burn
        self.cards_to_reveal = cards_to_reveal

    def start(self) -> None:
        self._deal([self.game._discard_pile], count=self.cards_to_burn)
        self._deal([self.game._community_pile], count=self.cards_to_reveal)
        self.game.end_step()
