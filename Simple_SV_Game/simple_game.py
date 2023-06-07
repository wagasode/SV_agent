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

def main():
    deck1 = Deck([Card(1, 1) for _ in range(20)])
    deck2 = Deck([Card(1, 1) for _ in range(20)])

    player1 = Player(20, deck1)
    player2 = Player(20, deck2)

    game = Game(player1, player2)

    while not game.is_game_over():
        card = game.current_player.draw_card()

        if card.cost <= game.turn:
            game.play_card(card)

        game.next_turn()

    if game.player1.life <= 0 or len(game.player1.deck.cards) == 0:
        print("Player 2 wins!")
    else:
        print("Player 1 wins!")

if __name__ == "__main__":
    main()

