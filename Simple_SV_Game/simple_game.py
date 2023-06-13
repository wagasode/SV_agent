import copy
from datetime import datetime
import json
import random

from mctspy.tree.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from mctspy.tree.search import MonteCarloTreeSearch
from mctspy.games.common import TwoPlayersAbstractGameState

class Card:
    def __init__(self, name, attack, cost):
        self.name = name
        self.attack = attack
        self.cost = cost

class Deck:
    def __init__(self, cards):
        self.cards = cards

    def draw_card(self):
        return self.cards.pop()

    def get_deck_num(self):
        return len(self.cards)

class Player:
    def __init__(self, deck, life=20):
        self.life = life
        self.deck = deck
        self.hand = []
        self.max_pp, self.temp_pp = 0, 0
        self.play_rule = 'random'

    def update_pp(self, turn):
        self.max_pp = turn
        self.temp_pp = self.max_pp

    def change_pp(self, variation):
        a = self.temp_pp
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

    def has_playable_cards(self):
        if len([card for card in self.hand if card.cost <= self.temp_pp]):
            return True
        return False

    def select_card_random(self):
        playable_cards = [card for card in self.hand if card.cost <= self.temp_pp]
        if random.random() < 1 / (len(playable_cards) + 1):
            return None
        selected_card = random.choice(playable_cards)
        return selected_card

# Gameの状態を表現する
class Game:
    def __init__(self, cards_data):
        self.CARDS_DATA = cards_data
        template_deck1 = self.create_template_deck(self.CARDS_DATA)
        template_deck2 = self.create_template_deck(self.CARDS_DATA)
        self.player1 = Player(template_deck1, 20)
        self.player2 = Player(template_deck2, 20)
        self.player2.play_rule = 'mcts'

        self.current_player = random.choice([self.player1, self.player2]) 
        self.opponent_player = self.player2 if self.current_player == self.player1 else self.player1
        self.second_player = self.opponent_player
        self.turn = 0
        self.winner = None
        self.real = True

        '''
        self.phase: int
        None: Game didn't start yet.
        0   : at_start_of_turn
        1   : in_turn
        2   : at_end_of_turn
        -1  : Game ended.
        '''
        self.phase = None
    
    def create_template_deck(self, cards_data):
        deck_cards = []
        # template_deck: card1:10, card2:10
        for card_data in cards_data:
            for _ in range(10):
                deck_cards.append(Card(card_data["name"], card_data["attack"], card_data["cost"]))
        random.shuffle(deck_cards)
        return Deck(deck_cards)

    def setup_game(self):
        print("="*20)
        print(" **  GAME START  ** ")
        print("="*20)
        for _ in range(3):
            drawn_card, _ = self.current_player.draw_card()
            drawn_card, _ = self.opponent_player.draw_card()
        self.turn = 1
        self.phase = 0

    def end_game(self):
        if self.winner == self.player1:
            print("="*25)
            print(" **  Player 1 wins!  ** ")
            print("="*25)
        else:
            print("="*25)
            print(" **  Player 2 wins!  ** ")
            print("="*25)

# GameStateを管理する
class GameManager():
    def __init__(self, game):
        self.game = game

    # 自動的にゲームを進行する
    def AutoGameStep(self):
        if self.game.phase == 0:
            return self.at_start_of_turn()
        if self.game.phase == 1:
            return self.in_turn()
        if self.game.phase == 2:
            return self.at_end_of_turn()

    # self.gameに受け取ったactionを適用する
    def ExecuteAction(self, action):
        if action == 'PASS':
            self.game.phase = 2
        else:
            # action: card_name(str)
            # cardをプレイした後のGameStateにする
            card = self.instanciate_card(action)
            if self.play_card(card):
                return True
            if not self.game.current_player.has_playable_cards():
                self.game.phase = 2
        return False

    def at_start_of_turn(self):
        self.display('turn')
        drawn_card, flag = self.game.current_player.draw_card()
        if flag:
            return True
        if drawn_card:
            self.display('draw_card', card=drawn_card)
        self.display('players_status')
        self.game.current_player.update_pp(self.game.turn)
        self.display('current_player_pp_update')
        self.display('current_player_hand')
        self.game.phase = 1
        return flag

    # phaseが進む条件==PASS
    def in_turn(self):
        if self.game.real:
            if self.game.current_player.play_rule == 'mcts':
                print('Selecting by mcts.')
                print('')
                new_game_state = self.execute_mcts(copy.deepcopy(self.game))
                self.game = new_game_state.game
                self.game.real = True
                print('update game state by mcts.')
                self.display('game')
                print()
                return False
        if self.game.current_player.play_rule == 'random':
            print('Selecting by random.')
            selected_card = self.game.current_player.select_card_random()
            if selected_card == None:
                # PASS -> phaseを進める
                self.game.phase = 2
                if self.game.real:
                    print('Player selected PASS.')
                return False
            self.display('play_card', card=selected_card)
            if self.play_card(selected_card):
                return True
            self.display('current_player_hand')
            if not self.game.current_player.has_playable_cards():
                # playable card is None -> phaseを進める
                self.game.phase = 2
                if self.game.real:
                    print('Player has no playable card.')
            return False

    def at_end_of_turn(self):
        self.game.current_player, self.game.opponent_player = self.game.opponent_player, self.game.current_player
        if self.game.current_player != self.game.second_player: 
            self.game.turn += 1
        if self.game.real:
            print()
        self.game.phase = 0
        return False

    def play_card(self, card):
        self.game.current_player.change_pp(-1*card.cost)
        self.display('current_player_pp_change', variation=-1*card.cost)
        self.game.current_player.hand.remove(card)
        self.game.opponent_player.take_damage(card.attack)
        return self.game.opponent_player.is_life_zero()
        
    def execute_mcts(self, game_state):
        now_state = GameStateForMCTS(game_state)
        root = TwoPlayersGameMonteCarloTreeSearchNode(state=now_state)
        mcts = MonteCarloTreeSearch(root)
        best_node = mcts.best_action(100)
        best_node.state.game_manager.display('game')
        return best_node.state

    def instanciate_card(self, card_name):
        for card in self.game.current_player.hand:
            if card.name == card_name:
                return card

    def display(self, command, card=None, variation=None):
        if self.game.real:
            if command == 'turn':
                print(f"Turn {self.game.turn}, Player {1 if self.game.current_player == self.game.player1 else 2}'s turn")
            elif command == 'players_status':
                for i, player in enumerate([self.game.player1, self.game.player2]):
                    print(f"Player {i+1}'s life: {player.life}, deck: {len(player.deck.cards)} cards")
            elif command == 'draw_card':
                print(f"Player {1 if self.game.current_player == self.game.player1 else 2} draws a card: {card.name} ({card.attack} attack, {card.cost} cost)")
            elif command == 'play_card':
                print(f"Player {1 if self.game.current_player == self.game.player1 else 2} plays a card: {card.name} ({card.attack} attack, {card.cost} cost)")
            elif command == 'current_player_hand':
                print(f"Player {1 if self.game.current_player == self.game.player1 else 2}'s hand: {[i.name for i in self.game.current_player.hand]}")
            elif command == 'current_player_pp_change':
                print(f"PP is changed {self.game.current_player.temp_pp - variation}/{self.game.current_player.max_pp} >>> {self.game.current_player.temp_pp}/{self.game.current_player.max_pp}")
            elif command == 'current_player_pp_update':
                print(f"PP is initialized: {self.game.current_player.temp_pp}/{self.game.current_player.max_pp}")
            elif command == 'game':
                print(f"Turn {self.game.turn}, Player {1 if self.game.current_player == self.game.player1 else 2}'s turn")
                for i, player in enumerate([self.game.player1, self.game.player2]):
                    print(f"Player {i+1}'s life: {player.life}, deck: {len(player.deck.cards)} cards")
                print(f"Player {1 if self.game.current_player == self.game.player1 else 2}'s hand: {[i.name for i in self.game.current_player.hand]}")
                print(f"Player {1 if self.game.opponent_player == self.game.player1 else 2}'s hand: {[i.name for i in self.game.opponent_player.hand]}")
                print(f"Player {1 if self.game.opponent_player == self.game.player1 else 2}'s PP is {self.game.current_player.temp_pp}/{self.game.current_player.max_pp}")

# MCTSの探索実行時に使用するGameのState
class GameStateForMCTS(TwoPlayersAbstractGameState):
    def __init__(self, game):
        self.game = game
        self.game_manager = GameManager(self.game)
        self.game.real = False
        self.next_to_move = 1 if self.game.current_player == self.game.player1 else -1

    def game_result(self):
        if self.game.winner == None:
            return None
        return 1 if self.game.winner == self.game.player1 else -1

    def is_game_over(self):
        return self.game_result() is not None

    def move(self, action):
        if self.game.phase in [0, 2]:
            _ = self.game_manager.AutoGameStep()
            return copy.deepcopy(self)
        else:
            new_game_state = copy.deepcopy(self)
            if new_game_state.game_manager.ExecuteAction(action):
                new_game_state.game.winner = new_game_state.game.current_player
            return new_game_state

    def get_legal_actions(self):
        playable_cards = [card.name for card in self.game.current_player.hand if card.cost <= self.game.current_player.temp_pp]
        playable_cards.append('PASS')
        return playable_cards

def main():
    json_file = 'cards.json'
    with open(json_file, 'r') as f:
        cards_data = json.load(f)['cards']

    game = Game(cards_data)
    game.setup_game()
    game_manager = GameManager(game)

    while True:
        if game_manager.AutoGameStep():
            break
    game.end_game()

if __name__ == "__main__":
    main()

