from collections import Counter

class Validator:
    def __init__(self):
        self.SCORES = {
            'royal_flush': 100,
            'four_of_a_kind': 50,
            'full_house': 30,
            'flush': 25,
            'straight': 20,
            'three_of_a_kind': 15,
            'two_pair': 10,
            'one_pair': 5,
            'none': 0
        }

    def evaluate_hand(self, cards, remaining_action_points):
        """
        Evaluates the player's hand, assigning the score.
        """
        combo_score = self.calculate_combo_score(cards)
        return combo_score + remaining_action_points

    def calculate_combo_score(self, cards):
        """
        Calculates the score of the hand combination according to the game rules.
        """
        straight_flush_score = self.evaluate_straights_flushes(cards)
        groups_score = self.evaluate_groups(cards)
        return max(straight_flush_score, groups_score)
    
    def evaluate_straights_flushes(self, cards):
        """
        Calls the methods to check if straights, flushes, or royal flushes are present.
        """
        numeric_cards = [c for c in cards if c.special_type is None]
        if len(numeric_cards) != 5:
            return 0

        if self.check_royal_flush(numeric_cards):
            return self.SCORES['royal_flush']
        if self.check_flush(numeric_cards):
            return self.SCORES['flush']
        if self.check_straight(numeric_cards):
            return self.SCORES['straight']
        
        return 0

    def evaluate_groups(self, cards):
        """
        Calls the methods to check if a four of a kind, full house, three of a kind,
        two pair, or one pair is present. If all are false, returns 0.
        """
        gem_score = self.handle_gem(cards)

        numeric_cards = [c for c in cards if c.special_type is None]
        if not numeric_cards:
            return gem_score

        normal_score = 0
        if self.check_four_of_a_kind(numeric_cards):
            normal_score = self.SCORES['four_of_a_kind']
        elif self.check_full_house(numeric_cards):
            normal_score = self.SCORES['full_house']
        elif self.check_three_of_a_kind(numeric_cards):
            normal_score = self.SCORES['three_of_a_kind']
        elif self.check_two_pair(numeric_cards):
            normal_score = self.SCORES['two_pair']
        elif self.check_one_pair(numeric_cards):
            normal_score = self.SCORES['one_pair']
        else:
            normal_score = 0
        
        return max(gem_score, normal_score)

    def handle_gem(self, cards):
        """
        Method to handle the special Gem card. The Gem is treated as a wild card
        that takes a value from 1 to 10 (no suit) to create or improve
        a combination among those listed in evaluate_groups. However, it cannot
        complete a straight, flush, or royal flush.
        """
        gems = [c for c in cards if c.special_type in ['G', 'Gem']]
        if not gems:
            return 0

        numeric_cards = [c for c in cards if c.special_type is None]
        values = [c.value for c in numeric_cards if c.value is not None]
        counts = Counter(values)

        if not counts:
            return 0

        num_gems = len(gems)

        if max(counts.values()) < 2:
            return 0

        best_score = 0

        for test_value in counts.keys():
            test_counts = counts.copy()
            test_counts[test_value] += num_gems

            sorted_counts = sorted(test_counts.values(), reverse=True)

            if sorted_counts[0] >= 4:
                score = self.SCORES['four_of_a_kind']
            elif sorted_counts[0] == 3 and len(sorted_counts) > 1 and sorted_counts[1] >= 2:
                score = self.SCORES['full_house']
            elif sorted_counts[0] == 3:
                score = self.SCORES['three_of_a_kind']
            elif sorted_counts[0] == 2 and len(sorted_counts) > 1 and sorted_counts[1] == 2:
                score = self.SCORES['two_pair']
            elif sorted_counts[0] == 2:
                score = self.SCORES['one_pair']
            else:
                score = 0

            if score > best_score:
                best_score = score

        return best_score

    def check_royal_flush(self, numeric_cards):
        """
        Method to check if the hand contains a royal flush.
        If there are 5 cards of the same suit and consecutive values (like 10, Jack, Queen, King, Ace),
        returns True.
        Note: In standard poker, a royal flush is 10, J, Q, K, A of the same suit.
        Here we check if 10 is in the values, and the high value is 14 (Ace), and the range of values is 5,
        which means 10, 11, 12, 13, 14.
        """
        if len(numeric_cards) != 5:
            return False
        
        suits = [c.suit for c in numeric_cards]
        if len(set(suits)) != 1:
            return False
        
        values = sorted([c.value for c in numeric_cards])
        if len(set(values)) != 5:
            return False
        
        if values[-1] - values[0] != 4:
            return False
        
        return 10 in values

    def check_four_of_a_kind(self, numeric_cards):
        """
        Method to check if the hand contains a four of a kind.
        If there are at least 4 cards of the same value, returns True.
        """
        values = [c.value for c in numeric_cards]
        counts = Counter(values)
        return max(counts.values()) >= 4 if counts else False

    def check_full_house(self, numeric_cards):
        """
        Method to check if the hand contains a full house.
        Checks that the highest frequency is 3 and the second highest is at least 2.
        """
        values = [c.value for c in numeric_cards]
        counts = Counter(values)
        sorted_counts = sorted(counts.values(), reverse=True)
        return len(sorted_counts) >= 2 and sorted_counts[0] == 3 and sorted_counts[1] >= 2
    
    def check_flush(self, numeric_cards):
        """
        Method to check if the hand contains a flush.
        If there are 5 cards of the same suit regardless of value, returns True.
        """
        if len(numeric_cards) != 5:
            return False
        
        suits = [c.suit for c in numeric_cards]
        return len(set(suits)) == 1

    def check_straight(self, numeric_cards):
        """
        Method to check if the hand contains a straight.
        If there are 5 cards in sequence regardless of suit, returns True.
        Also handles low straight (1, 2, 3, 4, 5) as a special case.
        """
        if len(numeric_cards) != 5:
            return False
        
        values = sorted([c.value for c in numeric_cards])
        if len(set(values)) != 5:
            return False
        
        if values[-1] - values[0] == 4:
            return True
        
        if values == [1, 2, 3, 4, 5]:
            return True
        
        return False

    def check_three_of_a_kind(self, numeric_cards):
        """
        Method to check if the hand contains a three of a kind.
        """
        values = [c.value for c in numeric_cards]
        counts = Counter(values)
        sorted_counts = sorted(counts.values(), reverse=True)
        return sorted_counts[0] == 3 if counts else False

    def check_two_pair(self, numeric_cards):
        """
        Method to check if the hand contains a two pair.
        """
        values = [c.value for c in numeric_cards]
        counts = Counter(values)
        sorted_counts = sorted(counts.values(), reverse=True)
        return len(sorted_counts) >= 2 and sorted_counts[0] == 2 and sorted_counts[1] == 2

    def check_one_pair(self, numeric_cards):
        """
        Method to check if the hand contains a pair.
        """
        values = [c.value for c in numeric_cards]
        counts = Counter(values)
        return max(counts.values()) >= 2 if counts else False
