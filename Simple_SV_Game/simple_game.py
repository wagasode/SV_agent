import random

class Card:
    id_counter = 0
    def __init__(self, name, attack, cost):
        self.name = name
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
        self.hand = []
        self.max_pp, self.temp_pp = 0, 0

    def init_play_point(self, turn):
        self.max_pp = turn
        self.temp_pp = self.max_pp
        print(f"PP is initialized: {self.temp_pp}/{self.max_pp}")

    def change_play_point(self, variation):
        a = self.temp_pp
        self.temp_pp += variation
        print(f"PP is changed {a}/{self.max_pp} >>> {self.temp_pp}/{self.max_pp}")

    def take_damage(self, damage):
        self.life -= damage

    def draw_card(self):
        card = self.deck.draw_card()
        self.hand.append(card)
        return card

    def select_play_card(self, remained_play_point):
        playable_cards = [card for card in self.hand if card.cost <= remained_play_point]
        while playable_cards:
            if random.random() < 1 / (len(playable_cards) + 1):
                print(f"Player selected PASS.")
                return None
            selected_card = random.choice(playable_cards)
            return selected_card

    def display_hand(self):
        print(f"Turn player's hand: {[card.name for card in self.hand]}")

class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.current_player = random.choice([self.player1, self.player2]) 
        self.opponent_player = self.player2 if self.current_player == self.player1 else self.player1
        self.second_player = self.opponent_player
        self.turn = 1
        random.shuffle(self.current_player.deck.cards)
        random.shuffle(self.opponent_player.deck.cards)
        
        print("="*20)
        print(" **  GAME START  ** ")
        print("="*20)

    def start_game(self):
        for player in [self.current_player, self.opponent_player]:
            for _ in range(3):
                player.draw_card()

    def next_turn(self):
        self.current_player, self.opponent_player = self.opponent_player, self.current_player
        if self.current_player != self.second_player: 
            self.turn += 1

    def is_game_over(self):
        return self.player1.life <= 0 or self.player2.life <= 0 or len(self.player1.deck.cards) == 0 or len(self.player2.deck.cards) == 0

    def play_card(self, card):
        if card.cost <= self.turn:
            self.current_player.hand.remove(card)
            self.opponent_player.take_damage(card.attack)

    def display_turn(self):
        print(f"Turn {self.turn}, Player {1 if self.current_player == self.player1 else 2}'s turn")

    def display_player_status(self):
        for i, player in enumerate([self.player1, self.player2]):
            print(f"Player {i+1}'s life: {player.life}, deck: {len(player.deck.cards)} cards")

    def display_draw_card(self, card):
        print(f"Player {1 if self.current_player == self.player1 else 2} draws a card: {card.name} ({card.attack} attack, {card.cost} cost)")

    def display_play_card(self, card):
        print(f"Player {1 if self.current_player == self.player1 else 2} plays a card: {card.name} ({card.attack} attack, {card.cost} cost)")

def main():
    deck1 = Deck([Card("Card1", 1, 1) for _ in range(10)] + [Card("Card2", 2, 2) for _ in range(10)])
    deck2 = Deck([Card("Card1", 1, 1) for _ in range(10)] + [Card("Card2", 2, 2) for _ in range(10)])

    player1 = Player(20, deck1)
    player2 = Player(20, deck2)

    game = Game(player1, player2)
    game.start_game()

    while not game.is_game_over():
        game.display_turn()
        game.display_player_status()

        card = game.current_player.draw_card()
        game.display_draw_card(card)
        game.current_player.display_hand()

        game.current_player.init_play_point(game.turn)
        while game.current_player.temp_pp > 0:
            selected_card = game.current_player.select_play_card(game.current_player.temp_pp)
            if selected_card:
                if selected_card.cost <= game.current_player.temp_pp:
                    print(f"cost: {selected_card.cost}, remained_pp: {game.current_player.temp_pp}/{game.current_player.max_pp}")
                    game.play_card(selected_card)
                    game.display_play_card(selected_card)
                    game.current_player.change_play_point(-1 * selected_card.cost)
                    game.current_player.display_hand()
            else:
                break
        game.next_turn()
        print()

    if game.player1.life <= 0 or len(game.player1.deck.cards) == 0:
        print("="*25)
        print(" **  Player 2 wins!  ** ")
        print("="*25)
    else:
        print("="*25)
        print(" ** Player 1 wins!  ** ")
        print("="*25)

if __name__ == "__main__":
    main()

