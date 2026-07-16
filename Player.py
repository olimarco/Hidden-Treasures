from Card import Card

class Player:
    """
    Represents a participant in the match. This class allows assigning a name,
    managing their hand of cards, Action Points, score tracking,
    and state—i.e., whether they have concluded the round or not.
    """
    def __init__(self, name):
        """
        Player constructor. Initializes the name and sets default values
        for the start of the match: empty hand, 15 Action Points, scores reset to zero,
        and round state as not concluded.
        """
        self._name = name
        self._hand = []
        self._action_points = 15
        self._score = 0
        self._total_score = 0
        self.concluded = False

    def add_card(self, card):
        """
        Checks that the player's hand is not already full (5 cards), and adds a card.
        """
        if len(self._hand) < 5:
            self._hand.append(card)

    def remove_card(self, card):
        """
        Removes a specific card from the player's hand.
        If the card is found and removed, the reset() method is invoked on it
        to clear its properties.
        If the card is not present, the exception is handled silently.
        """
        if len(self._hand) > 0:
            try:
                self._hand.remove(card)
                card.reset()
            except ValueError:
                return None

    """
    Below are all the getter and setter methods that allow accessing and modifying
    the Player class attributes from other files where it is imported.
    """
    @property
    def name(self):
        return self._name

    @property
    def hand(self):
        return self._hand

    @property
    def action_points(self):
        return self._action_points

    @action_points.setter
    def action_points(self, value):
        self._action_points = value

    @property
    def concluded(self):
        return self._concluded
    
    @concluded.setter
    def concluded(self, value):
        self._concluded = value

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    @property
    def total_score(self):
        return self._total_score

    @total_score.setter
    def total_score(self, value):
        self._total_score = value

    def reset_round(self):
        """
        Performs the cleanup operations necessary to start a new round.
        Resets all cards currently in hand (removing assignments and states),
        empties the hand list, restores the initial 15 Action Points,
        and sets the player as active (not concluded).
        """
        for card in self._hand:
            card.reset()
        self._hand = []
        self._action_points = 15
        self.concluded = False
