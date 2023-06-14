class Deck:
    def __init__(self, cards):
        self.cards = cards

    def draw_card(self):
        return self.cards.pop()

    def get_deck_num(self):
        return len(self.cards)
