Playing cards is a cards game, a standard deck of 54 cards contain 4 suit, clubs (♣), diamonds (♦), hearts (♥), spades (♠)., and 2 jokers.
Cards are "numbered"  Ace, 2,3,4,5,6,7,8,9,10,J,Q,K

# Deck
You can have a 52, 53, or 54 card deck
Some decks have 0 jokes, Some 1, Some 2 Joker, Joker are red and black 
Clubs and spades are black
Hearts and Diamond are Red

## Decks can be
Take card from specific position
Take a specific card from the deck
You can put a card back at a specific position
You can peek at a specific position (returns the card, but it remains in the deck)
You can get the current position of a card
You can cut a deck at a specific position
shuffled (ordered randomly)
    + different kinds of shuffling + chaining them !! THIS REQUIRES MULTIPLE SHUFFLERS
    "Different kinds of shuffling" raises the following question: do they give different results? The idea of shuffling is to end up with a randomly ordered deck. If we want to riffle the cards, what we're really asking is to to move the cards around in a specific fashion. It's like shuffling, but you provide your own mapping.


# Hands
Hands are sets  of cards. 
Hand can be for different  games, i,e Poker vs go fish, black jack (multiple decks)


## Hands can
be instantiated with specific cards, or empty
have cards added to them
have cards removed from them (by card)
have cards removed from them (by position)
be reordered (only important with visual interfaces)
compared to other hands (game-specific)

handle jokers; a joker can act as any other card or, presumably, have more complex rules applied to them. Jokers may need to become their own class of card.









#https://betandbeat.com/poker/blog/how-does-online-poker-deal-cards/
Each suited card in the deck is assigned a unique identifier (e.g., a number between 1 and 208)
Before the start of each hand, the deck is ‘created’ by using a random number generator, randomly ordering these numbers.
Once the deck has been built, the hand is then dealt as it would be in a live game with each player being given two cards, starting with the small blind.


When you first open a deck, you’ll usually see the Jokers at the face, followed by the Spades and Diamonds in ascending order, then the Clubs and Hearts in descending order. At the very back or top of the deck, you’ll get a few ad cards — or perhaps a double backer or gimmick card, depending on the deck.