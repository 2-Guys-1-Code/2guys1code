# Poker Game

We can start a game with X number of players
The game shuffles the deck then deals the hands, alternating between the players

players get chips
players can bet, call, raise, fold (implement betting rules)

We will need to implement some AIs for the computer to bet automatically
AND/OR
A way for humans to play


Round
    goes to winning / tying hand is determined
    players place bets or check or fold in squential order until 
Bet
Pot
Fold



Players can:
* check
* bet
* raise
* call
* fold


Simple steps:
* Simple game (no exchanging cards, no ante)  1 round only, winner player with most chips. No wild cards
    * all players check, reach the end, compare hands (no money in the pot, game will go on forever)
    * all players go all-in, reach the end, compare hands (winner takes all, game ends)
    * all players go all-in, reach the end, compare hands (TIE! split the pot) (2-way & 3-way tie)
    * first player goes all-in, all others fold. No comparison, only player left wins
    * all players raise small, then call when they don't have enough chips to raise


Ability to record/replay a game

## Wish list
### Rules / Mechanics
* Blinds
* Wildcards
** Specific cards and relative (lowest of the hand)
* Poker Rule sets
** Stud :checkmark:
** Draw poker :checkmark:
** Texas Hold'em "checkmark:
* Other Card games
** Go Fish
** Blackjack
* ...
### Infrastructure
* Server
* API / CLI
* GUI
* Synchronized store
* Spectator mode
** Win probability
* AI
* Security 
** Permissions
** Hidden data
* Persistence
* Save game & replay
### Meta
* Setting up open source
** Constitution and rules
*** The first goal of the project is to learn and to develop clean code & architecture
*** You are expected to use TDD
*** Aiming for 100% code coverage at all times
*** Comments are a code smell
* Hosting, etc.
** Domain
* CI /CD
** Style checks
** Version & vulnerability checks
** Static Code analysis
** Tests
* Git setup
** Branch protections
** PR checks (requires approval)
### Tech debt
* Hand Ranking engine


## Roadmap
1. Dockerize + ability to run tests inside
2. REST API
3. Basic GUI
4. Basic AI
5. Security & permissions
6. Spectator mode
7. Blinds



---


Write code to compare 2 hands of poker
Each hand has 5 cards, return the -1 if the first hand is better, 0 is they're equivalent, and 1 if the second hand is better

https://www.cardplayer.com/rules-of-poker/hand-rankings

1. Royal flush
A, K, Q, J, 10, all the same suit.
A K Q J T

2. Straight flush
Five cards in a sequence, all in the same suit.
8 7 6 5 4

3. Four of a kind
All four cards of the same rank.
J J J J 7

4. Full house
Three of a kind with a pair.
T T T 9 9

5. Flush
Any five cards of the same suit, but not in a sequence.
4 J 8 2 9

6. Straight
Five cards in a sequence, but not of the same suit.
9 8 7 6 5

7. Three of a kind
Three cards of the same rank.
7 7 7 K 3

8. Two pair
Two different pairs.
4 4 3 3 Q

9. Pair
Two cards of the same rank.
A A 8 4 7

10. High Card
When you haven't made any of the hands above, the highest card plays.
In the example below, the jack plays as the highest card.


We can start a game with X number of players
The game shuffles the deck then deals the hands, alternating between the players

players get chips (eventually, players can come with their own chips)
players can bet, call, raise, fold (implement betting rules)

We will need to implement some AIs for the computer to bet automatically
AND/OR
A way for humans to play

Draw Poker
if hand1> hand2:

Round
    goes to wining / tying hand is determined
    players place bets or check or fold in squential order until 
Bet
Pot
Fold



Players can:
* check
* bet
* raise
* call
* fold


Simple steps:
* Simple game (no exchanging cards, no ante)  1 round only, winner player with most chips. No wild cards
    * all players check, reach the end, compare hands (no money in the pot, game will go on forever)
    * all players go all-in, reach the end, compare hands (winner takes all, game ends)
    * all players go all-in, reach the end, compare hands (TIE! split the pot) (2-way & 3-way tie)
    * first player goes all-in, all others fold. No comparison, only player left wins
    * all players raise small, then call when they don't have enough chips to raise


Ability to record/replay a game