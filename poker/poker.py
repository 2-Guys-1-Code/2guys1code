from collections import Counter
import copy
from functools import partial
from itertools import groupby
from math import floor
from typing import Callable, Union

from card import Card
from deck import Deck
from card_collection import EmptyDeck, MissingCard
from hand import Hand
from player import AbstractPokerPlayer, Player
from poker_errors import (
    EndOfRound,
    EndOfStep,
    IllegalActionException,
    IllegalBetException,
    IllegalCardSwitch,
    InvalidAmountNegative,
    InvalidAmountNotAnInteger,
    TooManyPlayers,
)
from shuffler import AbstractShuffler, Shuffler
from turn import TurnManager


class Pot:
    bets: dict

    def __init__(self) -> None:
        self.bets = {}

    def add_bet(self, player: AbstractPokerPlayer, amount: int) -> None:
        if player not in self.bets:
            self.bets[player] = []

        self.bets[player].append(amount)

    def player_total(self, player: AbstractPokerPlayer) -> int:
        if player not in self.bets:
            return 0

        return sum(self.bets[player])

    def player_owed(self, player: AbstractPokerPlayer) -> int:
        if player not in self.bets:
            return self.max_player_total

        return self.max_player_total - self.player_total(player)

    def get_side_pots(self):
        players_per_total = {}
        for p in self.bets.keys():
            total = self.player_total(p)
            if total not in players_per_total:
                players_per_total[total] = []
            players_per_total[total].append(p)

        # {
        #     100: [p1],
        #     300: [p4],
        #     200: [p2, p3],
        # }

        totals = sorted(
            [(t, p) for t, p in players_per_total.items()], key=lambda x: x[0]
        )

        # [
        #     (100, [p1]),
        #     (200, [p2, p3]),
        #     (300, [p4]),
        # ]

        side_pots = []
        for i, (total, players) in enumerate(totals):
            all_players = players
            for j in range(i + 1, len(totals)):
                all_players.extend(totals[j][1])
            amount = total
            if i > 0:
                amount -= totals[i - 1][0]
            side_pots.append((amount, all_players))

        # [
        #     (100, [p1, p2, p3, p4]),
        #     (100, [p2, p3, p4]),
        #     (100, [p4]),
        # ]

        return side_pots

    @property
    def total(self) -> int:
        return sum([self.player_total(p) for p in self.bets.keys()])

    @property
    def max_player_total(self) -> int:
        return max([self.player_total(p) for p in self.bets.keys()], default=0)


class Poker:
    TYPE_BASIC: str = "BASIC"  # This should not be a thing anymore
    TYPE_STUD: str = "STUD"
    TYPE_DRAW: str = "DRAW"
    TYPE_HOLDEM: str = "HOLDEM"

    ACTION_CHECK: str = "CHECK"
    ACTION_BET: str = "BET"
    ACTION_CALL: str = "CALL"
    ACTION_FOLD: str = "FOLD"
    ACTION_ALLIN: str = "ALLIN"
    ACTION_RAISE: str = "RAISE"
    ACTION_SWITCH: str = "SWITCH"

    STEP_BETTING: str = "BETTING"
    STEP_DEAL: str = "DEAL"
    STEP_SWITCH: str = "SWITCH"
    STEP_REVEAL_FLOP: str = "REVEAL_FLOP"
    STEP_REVEAL_TURN: str = "REVEAL_TURN"


    _hands: list
    _deck: Deck
    _discard_pile: Hand

    _game_type: str
    _players: list[AbstractPokerPlayer]
    _round_players: list[AbstractPokerPlayer]
    kitty: int
    game_winner: Union[None, AbstractPokerPlayer]
    round_count: int
    step_count: int
    _shuffler: AbstractShuffler
    current_player: Union[None, AbstractPokerPlayer]

    def __init__(
        self,
        shuffler: AbstractShuffler = None,
        game_type: str = TYPE_STUD,
        pot_factory: Pot = Pot,
        hand_factory: Hand = Hand,
    ):
        self._game_type = game_type
        self._shuffler = shuffler or Shuffler()

        self._set_deck()
        self._set_round_steps()
        self._discard_pile = Hand()
        self._community_pile = Hand()
        self.pot_factory = pot_factory
        self.hand_factory = partial(hand_factory, _cmp=Poker.beats)

    def _set_deck(self) -> None:
        self._deck = Deck()

        self._deck.pull_card("RJ")
        self._deck.pull_card("BJ")

    # We should have a steps factory per game type that
    # returns the whole list of steps with their config
    def _step_factory(self, step: str) -> dict:
        if step == self.STEP_DEAL:
            if self._game_type == self.TYPE_HOLDEM:
                return {
                    "name": self.STEP_DEAL,
                    "config": {
                        "cards_per_player": 2,
                    },
                }
            else:
                return {
                    "name": self.STEP_DEAL,
                    "config": {
                        "cards_per_player": 5,
                    },
                }

        if step == self.STEP_BETTING:
            return {
                "name": self.STEP_BETTING,
                "actions": [
                    self.ACTION_ALLIN,
                    self.ACTION_BET,
                    self.ACTION_CALL,
                    self.ACTION_CHECK,
                    self.ACTION_FOLD,
                    self.ACTION_RAISE,
                ],
            }

        if step == self.STEP_SWITCH:
            return {
                "name": self.STEP_SWITCH,
                "actions": [
                    self.ACTION_SWITCH,
                ],
            }

        if step == self.STEP_REVEAL_FLOP:
            return {
                "name": self.STEP_REVEAL_FLOP,
                "config": {
                    "cards_to_burn": 1, 
                    "cards_to_reveal": 3,
                },
            }
        
        if step == self.STEP_REVEAL_TURN:
            return {
                "name": self.STEP_REVEAL_TURN,
                "config": {
                    "cards_to_burn": 1, 
                    "cards_to_reveal": 1,
                },
            }

    def _set_round_steps(self) -> None:
        self.steps = [
            self._step_factory(self.STEP_DEAL),
            self._step_factory(self.STEP_BETTING),
        ]

        if self._game_type == self.TYPE_DRAW:
            self.steps.append(self._step_factory(self.STEP_SWITCH))
            self.steps.append(self._step_factory(self.STEP_BETTING))

        if self._game_type == self.TYPE_HOLDEM:
            self.steps.append(self._step_factory(self.STEP_REVEAL_FLOP))
            self.steps.append(self._step_factory(self.STEP_BETTING))
            self.steps.append(self._step_factory(self.STEP_REVEAL_TURN))
            self.steps.append(self._step_factory(self.STEP_BETTING))

    def _distribute_chips(
        self, players: list[AbstractPokerPlayer], chips_per_player: int
    ) -> None:
        for p in players:
            p.add_to_purse(chips_per_player)

    def deal(
        self, players: list[AbstractPokerPlayer], deck: Deck, cards_per_player: int = 5
    ) -> None:
        self._shuffler.shuffle(self._deck)
        for _ in range(0, cards_per_player):
            for p in players:
                p.add_card(deck.pull_from_top())

    def deal_community_cards(
        self, deck: Deck, cards_to_burn: int = 0, cards_to_reveal: int = 0
    ) -> None:
        for _ in range(0, cards_to_burn):
            self._discard_pile.insert_at_end(deck.pull_from_top())

        for _ in range(0, cards_to_reveal):
            self._community_pile.insert_at_end(deck.pull_from_top())

    def start(
        self,
        chips_per_player: int,
        number_of_players: int = 0,
        players: list = None,
    ) -> None:
        if chips_per_player is None:
            chips_per_player = 500

        if players is not None:
            self._players = players
        else:
            self._players = [Player() for _ in range(number_of_players)]

            self._distribute_chips(
                self._players,
                chips_per_player,
            )

        for p in self._players:
            p.hand_factory = self.hand_factory

        self.kitty = 0
        self.round_count = 0
        self.game_winner = None
        self.current_player = None

    def _count_players_with_money(self) -> int:
        return len([p for p in self._players if p.purse > 0])

    def start_round(self) -> None:
        # I moved this here from end_round so we can assert the state at the end of the round;
        # Maybe it would be better to keep a list of rounds and the results and make
        # assertions on that instead of the live game state
        self._return_cards()

        if getattr(self, "_round_players", None):
            for p in self._round_players:
                if p.purse == 0:
                    self._players.remove(p)

        # TODO: Now we can just check the length of self._players
        if len(self._players) == 1:
            self.game_winner = self._players[0]

        self.round_count += 1
        self._round_players = self._players.copy()

        self.pot = self.pot_factory()

        self.step_count = 0
        self.init_step()

    def init_step(self) -> None:
        current_step = self.steps[self.step_count]
        self.action_count = 0
        self.nb_players_in_round = len(self._round_players)

        if current_step.get("name") == self.STEP_DEAL:
            self.current_player = None
            try:
                self.deal(
                    self._round_players, self._deck, **current_step.get("config", {})
                )
                self.end_step()
            except EmptyDeck as e:
                raise TooManyPlayers()
        if current_step.get("name") == self.STEP_REVEAL_FLOP or current_step.get("name") == self.STEP_REVEAL_TURN:
            self.current_player = None
            self.deal_community_cards(self._deck, **current_step.get("config", {}))
            self.end_step()
     
        else:
            self.current_player = self._round_players[0]

    def end_step(self) -> None:
        if self.step_count == len(self.steps) - 1:
            self.end_round()
            return

        self.step_count += 1
        self.init_step()

    def check_end_step(self) -> None:
        if len(self._round_players) == 1:
            raise EndOfStep()

        players_left = [
            p
            for p in self._round_players
            if self.pot.player_owed(p) != 0 and p.purse != 0
        ]

        if self.action_count >= self.nb_players_in_round and not len(players_left):
            raise EndOfStep()

    def maybe_end_step(self) -> None:
        try:
            self.check_end_step()
        except EndOfStep as e:
            self.end_step()
            raise EndOfStep()

    def end_round(self) -> None:
        self._distribute_pot()
        self.current_player = None

    def _transfer_to_pot(self, player: AbstractPokerPlayer, amount: int) -> None:
        if type(amount) is not int:
            raise InvalidAmountNotAnInteger()

        if amount < 0:
            raise InvalidAmountNegative()

        # TODO: Move take_from_purse inside add_bet?
        player.take_from_purse(amount)
        self.pot.add_bet(player, amount)

    def check(self, player: AbstractPokerPlayer) -> None:
        if self.pot.player_owed(player) != 0:
            raise IllegalActionException()

        with TurnManager(self, player, self.ACTION_CHECK):
            self.action_count += 1

    def all_in(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, self.ACTION_ALLIN):
            self.action_count += 1
            self._transfer_to_pot(player, player.purse)

    def fold(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, self.ACTION_FOLD):
            self.action_count += 1
            self._round_players.remove(player)

    def bet(self, player: AbstractPokerPlayer, bet_amount: int) -> None:
        if bet_amount < self.pot.player_owed(player):
            raise IllegalBetException()

        with TurnManager(self, player, self.ACTION_BET):
            self.action_count += 1
            self._transfer_to_pot(player, bet_amount)

    def call(self, player: AbstractPokerPlayer) -> None:
        with TurnManager(self, player, self.ACTION_CALL):
            self.action_count += 1
            bet_amount = self.pot.player_owed(player)
            self._transfer_to_pot(player, bet_amount)

    def raise_bet(self, player: AbstractPokerPlayer, bet_amount: int) -> None:
        with TurnManager(self, player, self.ACTION_RAISE):
            self.action_count += 1
            self._transfer_to_pot(player, self.pot.player_owed(player) + bet_amount)

    def _can_switch_cards(self, hand: Hand, cards_to_switch: list) -> bool:
        has_ace = {Card("1H"), Card("1D"), Card("1S"), Card("1C")}.intersection(
            {c for c in hand}
        )
        if (not has_ace and len(cards_to_switch) > 3) or len(cards_to_switch) > 4:
            return False

        for card in cards_to_switch:
            if not card in hand:

                return False

        return True

    def switch_cards(self, player: Player, cards_to_switch: list) -> None:
        with TurnManager(self, player, self.ACTION_SWITCH):
            if not self._can_switch_cards(player.hand, cards_to_switch):
                raise IllegalCardSwitch()

            self.action_count += 1
            for card in cards_to_switch:
                self._discard_pile.insert_at_end(player.hand.pull_card(card))
                player.add_card(self._deck.pull_from_top())

    def _distribute_pot(self) -> None:
        side_pots = self.pot.get_side_pots()
        for side_pot in side_pots:
            elligible = list(set(side_pot[1]).intersection(self._round_players))
            winners = self.find_winnner(elligible)
            amount = side_pot[0] * len(side_pot[1])
            chips_per_winner = floor(amount / len(winners))
            for p in winners:
                p.add_to_purse(chips_per_winner)

            self.kitty += amount - (chips_per_winner * len(winners))

        self.pot = None

    def _return_cards(self):
        for p in self._players:
            for i in range(len(p.hand), 0, -1):
                card = p.hand.pull_from_position(i)
                self._deck.insert_at_end(card)

    def find_winnner(
        self, players: list[AbstractPokerPlayer]
    ) -> list[AbstractPokerPlayer]:
        p1 = players[0]
        winners = [p1]

        for p2 in players[1:]:
            if p2.hand == p1.hand:
                winners.append(p2)
            elif p2.hand > p1.hand:
                p1 = p2
                winners = [p2]

        return winners

    @staticmethod
    def beats(hand_1: list, hand_2: list) -> int:
        hand_1 = Poker._parse_to_cards(hand_1).copy()
        hand_2 = Poker._parse_to_cards(hand_2).copy()

        ordered_tests = [
            Poker._straight_flush_test,
            Poker._four_of_a_kind_test,
            Poker._full_house_test,
            Poker._flush_test,
            Poker._straight_test,
            Poker._three_of_a_kind_test,
            Poker._two_pair_test,
            Poker._pair_test,
            Poker._high_card_test,
        ]
        for test in ordered_tests:
            winner = test(hand_1, hand_2)
            # winning_test = test.__name__
            if winner != 0:
                break

        return winner

    @staticmethod
    def _parse_to_cards(hand) -> list:
        _eq = lambda s, b: s.rank == b.rank
        _hash = lambda s: s.rank
        return [Card(c, _eq=_eq, _hash=_hash) for c in hand]

    @staticmethod
    def _straight_flush_test(hand_1: list, hand_2: list) -> int:
        first_card = Poker._extract_straight_flush(hand_1)
        second_card = Poker._extract_straight_flush(hand_2)

        if first_card is None and second_card is None:
            return 0

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _four_of_a_kind_test(hand_1: list, hand_2: list) -> int:
        first_card = Poker._find_set(hand_1, 4)
        second_card = Poker._find_set(hand_2, 4)

        if first_card is None and second_card is None:
            return 0

        if first_card is not None:
            Poker._remove_cards_by_rank(hand_1, first_card)

        if second_card is not None:
            Poker._remove_cards_by_rank(hand_2, second_card)

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _full_house_test(hand_1: list, hand_2: list) -> int:
        cards_1 = Poker._extract_full_house(hand_1)
        cards_2 = Poker._extract_full_house(hand_2)

        if cards_1 is None and cards_2 is None:
            return 0

        if cards_1 is None:
            return -1

        if cards_2 is None:
            return 1

        if cards_1[0] > cards_2[0]:
            return 1
        if cards_1[0] < cards_2[0]:
            return -1

        if cards_1[1] > cards_2[1]:
            return 1
        if cards_1[1] < cards_2[1]:
            return -1

        return 0

    @staticmethod
    def _flush_test(hand_1: list, hand_2: list) -> int:
        first_card = Poker._extract_flush(hand_1)
        second_card = Poker._extract_flush(hand_2)

        if first_card is None and second_card is None:
            return 0

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _straight_test(hand_1: list, hand_2: list) -> int:
        first_card = Poker._extract_straight(hand_1)
        second_card = Poker._extract_straight(hand_2)

        if first_card is None and second_card is None:
            return 0

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _three_of_a_kind_test(hand_1: list, hand_2: list) -> int:
        first_card = Poker._find_set(hand_1, 3)
        second_card = Poker._find_set(hand_2, 3)

        if first_card is None and second_card is None:
            return 0

        if first_card is not None:
            Poker._remove_cards_by_rank(hand_1, first_card)

        if second_card is not None:
            Poker._remove_cards_by_rank(hand_2, second_card)

        if first_card > second_card:
            return 1
        if second_card > first_card:
            return -1
        return 0

    @staticmethod
    def _two_pair_test(hand_1: list, hand_2: list) -> int:
        cards_1 = Poker._find_two_pair(hand_1)
        cards_2 = Poker._find_two_pair(hand_2)

        if cards_1 is None and cards_2 is None:
            return 0

        if cards_1 is None:
            return -1

        if cards_2 is None:
            return 1

        if cards_1[0] > cards_2[0]:
            return 1
        if cards_1[0] < cards_2[0]:
            return -1

        if cards_1[1] > cards_2[1]:
            return 1
        if cards_1[1] < cards_2[1]:
            return -1

        return 0

    @staticmethod
    def _pair_test(hand_1: list, hand_2: list) -> int:
        first_card = Poker._find_set(hand_1, 2)
        other_card = Poker._find_set(hand_2, 2)

        if first_card is None and other_card is None:
            return 0

        if first_card is not None:
            Poker._remove_cards_by_rank(hand_1, first_card)

        if other_card is not None:
            Poker._remove_cards_by_rank(hand_2, other_card)

        if first_card > other_card:
            return 1
        if other_card > first_card:
            return -1
        return 0

    @staticmethod
    def _high_card_test(hand_1: list, hand_2: list) -> int:
        while True:
            first_card = max(hand_1, default=None)
            other_card = max(hand_2, default=None)

            if first_card is None and other_card is None:
                return 0

            hand_1.remove(first_card)
            hand_2.remove(other_card)

            if first_card > other_card:
                return 1
            elif first_card < other_card:
                return -1

    @staticmethod
    def _extract_straight_flush(hand: list) -> Union[Card, None]:
        hand.sort()
        for x in range(1, len(hand)):
            if hand[x - 1].rank != hand[x].rank - 1:
                return None
            if hand[x - 1].suit != hand[x].suit:
                return None

        return hand[0]

    @staticmethod
    def _extract_straight_flush__v2(hand: list) -> Union[Card, None]:
        hand.sort()
        new_hand = []
        for x in range(1, len(hand)):
            if hand[x - 1].rank != hand[x].rank - 1:
                new_hand = []
                continue
            if hand[x - 1].suit != hand[x].suit:
                new_hand = []
                continue

            if len(hand) - x < 5:
                # Not enough cards left to build a straight flush
                return None
            
            new_hand.append(hand[x])

        if len(new_hand) == 5:
            return new_hand

        return None

    @staticmethod
    def _extract_full_house(hand: list) -> Union[list, None]:
        triple = Poker._find_set(hand, 3)
        pair = Poker._find_set(hand, 2)

        if triple is None or pair is None:
            return None

        return [triple, pair]

    @staticmethod
    def _extract_flush(hand: list) -> Union[Card, None]:
        for x in range(1, len(hand)):
            if hand[x - 1].suit != hand[x].suit:
                return None

        return hand[0]

    @staticmethod
    def _extract_straight(hand: list) -> Union[Card, None]:
        hand.sort()
        for x in range(1, len(hand)):
            if hand[x - 1].rank != hand[x].rank - 1:
                return None

        return hand[0]

    @staticmethod
    def _find_set(hand: list, set_size: int) -> Union[Card, None]:
        sets = [k for k, v in Counter(hand).items() if v == set_size]
        if len(sets) == 0:
            return None

        return max(sets, default=None)

    @staticmethod
    def _remove_cards_by_rank(hand: list, rank_card: Card) -> None:
        for x in range(len(hand) - 1, -1, -1):
            if hand[x].rank == rank_card.rank:
                hand.pop(x)

    @staticmethod
    def _find_two_pair(hand: list) -> Union[list, None]:
        pairs = [k for k, v in Counter(hand).items() if v == 2]
        if len(pairs) < 2:
            return None

        pairs.sort(reverse=True)
        for x in range(len(hand) - 1, -1, -1):
            if hand[x].rank == pairs[0].rank or hand[x].rank == pairs[1].rank:
                hand.pop(x)
        return [pairs[0], pairs[1]]

    @staticmethod
    def _reindex_card(card: int) -> int:
        return ((card - 2 + 13) % 13) + 2

    @staticmethod
    def _reindex_hand(hand: list) -> list:
        return [Poker._reindex_card(c) for c in hand]
