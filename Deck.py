from Card import Card
from random import shuffle

class Deck:
    """
    Represents the game deck. Manages the creation of standard and special
    Card instances, shuffling, and drawing cards to place on the game grid.
    """
    def __init__(self):
        """
        Initializes the base configurations (list of suits, types of special cards,
        and numeric value range) and prepares the empty container for cards.
        """
        self._deck = []
        self._suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
        self._special_cards = ["Coin", "Scroll", "Gem"]
        self._values = (1, 14)

    def create_deck(self):
        """
        Fills the deck by generating all instances of the Card class.
        Creates numeric cards for each suit and adds unique special cards.
        After generation, automatically shuffles the deck.
        """
        self._deck = []
        for i in range(*self._values):
            for j in self._suits:
                c = Card(value=i, suit=j)
                self._deck.append(c)
        for i in self._special_cards:
            c = Card(special_type=i)
            self._deck.append(c)
        self.shuffle()

    def shuffle(self):
        """
        Checks if the deck contains cards and shuffles them randomly
        using the shuffle algorithm.
        """
        if self._deck:
            shuffle(self._deck)

    def draw_36(self):
        """
        Draws and returns the first 36 cards from the deck, required to fill the 6x6
        game grid. The drawn cards are removed from the deck's main list.
        Returns an empty list if the deck contains fewer than 36 cards.
        """
        if len(self._deck) < 36:
            return []
        drawn_cards = self._deck[:36]
        self._deck = self._deck[36:]
        return drawn_cards

    def __str__(self):
        """
        Returns an informative string indicating how many cards are currently
        left in the deck. Mainly useful for debugging.
        """
        return f"Deck with {len(self._deck)} cards"
