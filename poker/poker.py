from collections import Counter
import copy
from math import floor
from typing import Callable, Union

from card import Card
from deck import Deck
from hand import Hand
from player import AbstractPokerPlayer, Player
from poker_errors import NotEnoughChips, PlayerOutOfOrderException
from shuffler import AbstractShuffler, Shuffler


class Poker:
    CARDS_PER_HAND: int = 5

    TYPE_BASIC: str = "BASIC"
    TYPE_STANDARD: str = "STANDARD"

    ACTION_CHECK: str = "CHECK"
    ACTION_BET: str = "BET"
    ACTION_CALL: str = "CALL"
    ACTION_FOLD: str = "FOLD"
    ACTION_ALLIN: str = "ALLIN"
    ACTION_RAISE: str = "RAISE"

    _hands: list
    _deck: Deck

    chips_in_game: int
    chips_in_bank: int
    _game_type: str
    _players: list[AbstractPokerPlayer]
    _round_players: list[AbstractPokerPlayer]
    kitty: int
    game_winner: Union[None, AbstractPokerPlayer]
    round_count: int
    _shuffler: AbstractShuffler

    def __init__(
        self, shuffler: AbstractShuffler = None, game_type: str = TYPE_STANDARD
    ):
        self._game_type = game_type
        self._shuffler = shuffler or Shuffler()

        self._set_deck()

        # Todo: fix this; test bad? distibute pot? one source of truth
        self.kitty = 0
        self.round_count = 0
        self.game_winner = None

    def _set_deck(self):
        if self._shuffler is not None:
            self._deck = Deck(shuffler=self._shuffler)
        else:
            self._deck = Deck()

        if self._game_type == self.TYPE_STANDARD:
            self._deck.pull_card("RJ")
            self._deck.pull_card("BJ")

    def _distribute_chips(self, chips_per_player):
        for p in self._players:
            p.add_to_purse(chips_per_player)
            self.chips_in_bank -= chips_per_player
            if self.chips_in_bank < 0:
                raise NotEnoughChips()

    def deal(self):
        for _ in range(0, self.CARDS_PER_HAND):
            for p in self._players:
                # We don't necessary love this.....
                if p.hand is None:
                    p.hand = Hand(_cmp=Poker.beats)
                p.hand.insert_at_end(self._deck.pull_from_top())

    @property
    def _player_count(self):
        return len(self._players)

    def start(
        self,
        number_of_players: int = 0,
        total_chips: int = 0,
        chips_per_player: int = 500,
        players: list = None,
    ) -> None:

        self.chips_in_bank = 0
        self.chips_in_game = 0

        if players is not None:
            self._players = players
            self.chips_in_bank = 0
            self.chips_in_game = sum([p.purse for p in self._players])

        else:
            self._players = [Player() for _ in range(number_of_players)]
            self.chips_in_bank = self.chips_in_game = (
                chips_per_player * self._player_count
                if total_chips == 0
                else total_chips
            )

            self._distribute_chips(chips_per_player)

        self.kitty = 0
        self._round_players = self._players.copy()

    def _get_method(self, action: str = None) -> Callable[[AbstractPokerPlayer], None]:
        if action == self.ACTION_ALLIN:
            return self.all_in
        elif action == self.ACTION_FOLD:
            return self.fold

        # if action == self.ACTION_CHECK:
        return self.check

    def _count_players_with_money(self) -> int:
        return len([p for p in self._players if p.purse > 0])

    def start_round(self) -> None:
        self.round_count += 1

        self.current_player = 0
        self._shuffler.shuffle(self._deck)
        self.deal()

    def play(self) -> None:
        self.pot = 0
        while self.game_winner is None and self.round_count < 2:
            self.start_round()

            for player in self._players:
                print(player._hand)

                action = player.get_action(self)
                method = self._get_method(action)
                method(player)

                # Make this better when we introduce more rounds
                if len(self._round_players) == 1:
                    self.winner = self._round_players[0]
                    self.winning_hand = self.winner.hand

                    self._distribute_pot([self.winner])
                    return

            winners = self.find_winnner()
            print(winners)
            self.winner = self._players[winners[0]]
            self.winning_hand = copy.deepcopy(self.winner.hand)
            self._distribute_pot([self._players[i] for i in winners])
            self._return_cards()
            if self._count_players_with_money() == 1:
                print("here")
                self.game_winner = self.winner

            print(self.round_count)

    # self._distribute_pot([self._players[i] for i in winners])

    def check(self, player: AbstractPokerPlayer) -> None:
        # todo: are they allowed to check? (a.k.a. is there money "pending")

        if self._round_players.index(player) != self.current_player:
            raise PlayerOutOfOrderException()

        self.current_player += 1

        if self.current_player >= len(self._round_players):
            self.current_player = 0

    def all_in(self, player: AbstractPokerPlayer) -> None:
        if self._round_players.index(player) != self.current_player:
            raise PlayerOutOfOrderException()

        self.current_player += 1

        if self.current_player >= len(self._round_players):
            self.current_player = 0

        # self.pot += player.remove_from_purse(player.purse)
        self.pot += player.purse
        player.purse = 0

    def fold(self, player: AbstractPokerPlayer) -> None:
        # TODO: Third time we duplicate this!!!! CONTEXT MANAGER!!!!! With playerTurn!!!!
        if self._round_players.index(player) != self.current_player:
            raise PlayerOutOfOrderException()

        self._round_players.remove(player)

        if self.current_player >= len(self._round_players):
            self.current_player = 0

    def _distribute_pot(self, winners: list[AbstractPokerPlayer]) -> None:
        if len(winners) == 0:
            return

        chips_per_winner = floor(self.pot / len(winners))
        for p in winners:
            p.add_to_purse(chips_per_winner)
            self.pot -= chips_per_winner

        self.kitty += self.pot
        self.pot = 0

    def _return_cards(self):
        for p in self._players:
            for i in range(len(p._hand), 0, -1):
                card = p._hand.pull_from_position(i)
                self._deck.insert_at_end(card)

            print(p._hand)

        print(len(self._deck))

    def find_winnner(self) -> list[int]:
        p1 = self._round_players[0]
        winners = [0]
        for i, p2 in enumerate(self._round_players[1:]):

            if p2.hand == p1.hand:
                winners.append(i + 1)
            elif p2.hand > p1.hand:
                p1 = p2
                winners = [i + 1]

        return winners

    @staticmethod
    def beats(hand_1: list, hand_2: list) -> int:
        hand_1 = Poker._parse_to_cards(hand_1)
        hand_2 = Poker._parse_to_cards(hand_2)

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
            winning_test = test.__name__
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
        first_card = max(hand_1, default=None)
        other_card = max(hand_2, default=None)

        if first_card is None and other_card is None:
            return 0

        if first_card > other_card:
            return 1
        elif first_card < other_card:
            return -1
        return 0

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
