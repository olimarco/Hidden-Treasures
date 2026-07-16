class Card:
    """
    Represents a playing card, which can be a standard card (value and suit)
    or a special card (Coin, Gem, or Scroll). It also manages the card's state
    (face down/face up).
    """
    def __init__(self, value=None, suit=None, special_type=None):
        """
        Takes value and suit, or special type as arguments,
        and creates the respective attributes, as well as the attributes needed
        to manage the other characteristics of the card.
        """
        self._value = value
        self._suit = suit
        self._special_type = special_type
        self._face_down = True
        self._revealed_permanently = False

    def __str__(self):
        """
        Returns a text representation of the card.
        It also handles the numerical values of the face cards (Jack, Queen, King, Ace)
        and special cards.
        """
        if self._special_type:
            return f"{self._special_type}"
        elif self._value and self._suit:
            faces = {11: "Jack", 12: "Queen", 13: "King", 14: "Ace"}
            if self._value in faces:
                return f"{faces[self._value]} of {self._suit}"
            else:
                return f"{self._value} of {self._suit}"
        return "Invalid card"
    
    """
    Below are all the getters and setters used to easily access and modify
    card values from other files.
    """
    @property
    def value(self):
        return self._value

    @property
    def suit(self):
        return self._suit

    @property
    def special_type(self):
        return self._special_type
    
    @property
    def revealed_permanently(self):
        return self._revealed_permanently

    def flip_card(self):
        """
        Inverts the visibility state of the card (from face down to face up and vice versa).
        The action is blocked if the card has been permanently revealed by the scroll.
        """
        if not self._revealed_permanently:
            self._face_down = not self._face_down

    def reveal_permanently(self):
        """
        Sets the card state as permanently revealed and "reveals the card",
        allowing the GUI to easily handle the scroll functionality.
        """
        self._revealed_permanently = True
        self._face_down = False

    def reset(self):
        """
        Resets the card's initial conditions.
        """
        self._face_down = True
        self._revealed_permanently = False
