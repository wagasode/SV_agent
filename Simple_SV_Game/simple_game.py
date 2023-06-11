import json
import random

from mctspy.tree.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from mctspy.tree.search import MonteCarloTreeSearch
from mctspy.games.common import TwoPlayersGameState

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
    def __init__(self, deck, life=20):
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

    def select_action_mcts(self, game_state):
        mcts = MCTS(game_state)
        best_action = mcts.search()
        return best_action

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
        
        print("="*20)
        print(" **  GAME START  ** ")
        print("="*20)

    def load_cards_from_json(self, json_file):
        with open(json_file, 'r') as f:
            cards_data = json.load(f)
        return cards_data

    def create_deck(self, cards_data):
        deck_cards = []
        for card_data in cards_data:
            for _ in range(10):
                deck_cards.append(Card(card_data["name"], card_data["attack"], card_data["cost"]))
        random.shuffle(deck_cards)
        return Deck(deck_cards)

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

class GameState(TwoPlayersGameState):
    def __init__(self, next_to_move=1):
        self.cards_data = self.load_cards_from_json('cards.json')['cards']
        deck1 = self.create_deck(self.cards_data)
        deck2 = self.create_deck(self.cards_data)
        self.player1 = Player(deck1)
        self.player2 = Player(deck2)

        self.state = {}
        self.state['player1'] = player1
        self.state['player2'] = player2
        self.next_to_move = next_to_move
        self.winner = None

    def game_over(self):
        # ゲームが終了した時に行われる処理
        if self.winnter == self.player1:
            print("="*25)
            print(" **  Player 1 wins!  ** ")
            print("="*25)
        else:
            print("="*25)
            print(" **  Player 2 wins!  ** ")
            print("="*25)

    def is_game_over(self):
        if is_game_over_with_life() or is_game_over_with_life():
            return True
        return False

    def is_game_over_with_life(self):
        if self.state['player1'].life <= 0:
            self.winner = player2
            return True
        if self.state['player2'].life <= 0:
            self.winner = player1
            return True
        return False

    def is_game_over_with_draw(self, drawing_player):
        if len(drawing_player.deck) <= 0:
            self.winner = opponent_player(drawing_player)
            return True
        return False

    def opponent_player(self, current_player):
        if current_player == self.player1:
            return self.player2
        else:
            return self.player1

    def move(self, action):
        # 指定された行動を実行
        pass

    def get_legal_actions(self):
        # 可能な行動のリスト
        pass

def main():

    initial_state = GameState()

    game = Game(initial_state.player1, initial_state.player2)
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

    # ゲームの初期状態を作成
    initial_state = CardGameState(state=...)

    # 初期状態を用いてMCTSのルートノードを作成
    root = TwoPlayersGameMonteCarloTreeSearchNode(state=initial_state)

    # MCTSを実行
    mcts = MonteCarloTreeSearch(root)
    best_node = mcts.best_action(1000)

if __name__ == "__main__":
    main()

