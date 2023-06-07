class Card:
    def __init__(self, attack, cost):
        self.attack = attack
        self.cost = cost

class Deck:
    def __init__(self, cards):
        self.cards = cards

    def draw_card(self):
        return self.cards.pop()

class Player:
    def __init__(self, life, deck):
        self.life = life
        self.deck = deck

    def take_damage(self, damage):
        self.life -= damage

    def draw_card(self):
        return self.deck.draw_card()

class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.opponent_player = player2
        self.turn = 1

    def next_turn(self):
        self.current_player, self.opponent_player = self.opponent_player, self.current_player
        self.turn += 1

    def is_game_over(self):
        return self.player1.life <= 0 or self.player2.life <= 0 or len(self.player1.deck.cards) == 0 or len(self.player2.deck.cards) == 0

    def play_card(self, card):
        if card.cost <= self.turn:
            self.opponent_player.take_damage(card.attack)

