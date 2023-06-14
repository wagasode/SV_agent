import random


class Player:
    def __init__(self, deck, life=20, is_user_controlled=False):
        self.life = life
        self.deck = deck
        self.hand = []
        self.max_pp, self.temp_pp = 0, 0
        self.play_rule = "random"
        self.is_user_controlled = is_user_controlled

    def update_pp(self, turn):
        self.max_pp = turn
        self.temp_pp = self.max_pp

    def change_pp(self, variation):
        self.temp_pp += variation

    def take_damage(self, damage):
        self.life -= damage

    def is_life_zero(self):
        return self.life <= 0

    def draw_card(self):
        if not self.deck.get_deck_num():
            return None, True
        card = self.deck.draw_card()
        self.hand.append(card)
        return card, False

    def get_playable_cards(self):
        return [card for card in self.hand if card.cost <= self.temp_pp]

    def has_playable_cards(self):
        if len(self.get_playable_cards()):
            return True
        return False

    def select_card_random(self):
        playable_cards = self.get_playable_cards()
        if random.random() < 1 / (len(playable_cards) + 1):
            return None
        selected_card = random.choice(playable_cards)
        return selected_card
