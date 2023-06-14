import copy
import random

import numpy as np

from player_attributes import Player

from mctspy.tree.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from mctspy.tree.search import MonteCarloTreeSearch
from mctspy.games.common import TwoPlayersAbstractGameState


# Gameの状態を表現する
class Game:
    def __init__(self, decks, mode="1"):
        self.player1 = Player(decks[0], 20)
        if mode == "2":
            self.player2 = Player(decks[1], 20, is_user_controlled=True)
            self.player2.play_rule = "mcts"
        else:
            self.player2 = Player(decks[1], 20)

        self.current_player = random.choice([self.player1, self.player2])
        self.opponent_player = (
            self.player2 if self.current_player == self.player1 else self.player1
        )
        self.second_player = self.opponent_player
        self.turn = 0
        self.winner = None
        self.real = True

        """
        self.phase: int
        None: Game didn't start yet.
        0   : at_start_of_turn
        1   : in_turn
        2   : at_end_of_turn
        -1  : Game ended.
        """
        self.phase = None

    def setup_game(self):
        print("=" * 20)
        print(" **  GAME START  ** ")
        print("=" * 20)
        for _ in range(3):
            drawn_card, _ = self.current_player.draw_card()
            drawn_card, _ = self.opponent_player.draw_card()
        self.turn = 1
        self.phase = 0

    def end_game(self):
        if self.winner == self.player1:
            print("=" * 25)
            print(" **  Player 1 wins!  ** ")
            print("=" * 25)
        elif self.winner == self.player2:
            print("=" * 25)
            print(" **  Player 2 wins!  ** ")
            print("=" * 25)
        else:
            print("=" * 25)
            print(" **  No winner.  ** ")
            print("=" * 25)


# GameStateを管理する
class GameManager:
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
        if action == "PASS":
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
        self.display("turn")
        drawn_card, flag = self.game.current_player.draw_card()
        if flag:
            return True
        if drawn_card:
            self.display("draw_card", card=drawn_card)
        self.display("players_status")
        self.game.current_player.update_pp(self.game.turn)
        self.display("current_player_pp_update")
        self.display("current_player_hand")
        self.game.phase = 1
        return flag

    # phaseが進む条件==PASS
    def in_turn(self):
        if self.game.real:
            if self.game.current_player.is_user_controlled:
                print("Select your play card!")
                self.display("current_player_hand")
                if self.game.current_player.has_playable_cards():
                    playable_cards = self.game.current_player.get_playable_cards()
                    print(
                        f"Your playable cards: {[card.name for card in playable_cards]}"
                    )
                    selected_card_num = int(
                        input("Enter the number of card: 0 is PASS.")
                    )
                    if selected_card_num == 0:
                        self.game.phase = 2
                        print("You selected PASS.")
                        return False
                    selected_card = playable_cards[selected_card_num - 1]
                    self.display("play_card", card=selected_card)
                    if self.play_card(selected_card):
                        self.game.winner = self.game.current_player
                        return True
                    self.display("current_player_hand")
                    if not self.game.current_player.has_playable_cards():
                        self.game.phase = 2
                        if self.game.real:
                            print("You has no playable cards! Must PASS.")
                    return False
                else:
                    print("You have no playable cards! Must PASS.")
                    self.game.phase = 2
                    return False
            if self.game.current_player.play_rule == "mcts":
                print("Selecting by mcts.")
                print("")
                new_game_state = self.execute_mcts(copy.deepcopy(self.game))
                self.game = new_game_state.game
                self.game.real = True
                print("update game state by mcts.")
                self.display("game")
                print()
                if self.game.current_player.life <= 0:
                    self.game.winner == self.game.opponent_player
                    return True
                if self.game.opponent_player.life <= 0:
                    self.game.winner == self.game.current_player
                    return True
                return False
        if self.game.current_player.play_rule == "random":
            print("Selecting by random.")
            selected_card = self.game.current_player.select_card_random()
            if selected_card is None:
                # PASS -> phaseを進める
                self.game.phase = 2
                if self.game.real:
                    print("Player selected PASS.")
                return False
            self.display("play_card", card=selected_card)
            if self.play_card(selected_card):
                self.game.winner = self.game.current_player
                return True
            self.display("current_player_hand")
            if not self.game.current_player.has_playable_cards():
                # playable card is None -> phaseを進める
                self.game.phase = 2
                if self.game.real:
                    print("Player has no playable card.")
            return False

    def at_end_of_turn(self):
        self.game.current_player, self.game.opponent_player = (
            self.game.opponent_player,
            self.game.current_player,
        )
        if self.game.current_player != self.game.second_player:
            self.game.turn += 1
        if self.game.real:
            print()
        self.game.phase = 0
        return False

    def play_card(self, card):
        self.game.current_player.change_pp(-1 * card.cost)
        self.display("current_player_pp_change", variation=-1 * card.cost)
        self.game.current_player.hand.remove(card)
        self.game.opponent_player.take_damage(card.attack)
        self.display("players_status")
        return self.game.opponent_player.is_life_zero()

    def execute_mcts(self, game_state):
        now_state = GameStateForMCTS(game_state)
        root = MyMCTSNode(state=now_state)
        mcts = MyMCTS(root)
        best_node = mcts.best_action(10)
        best_node.state.game_manager.display("game")
        return best_node.state

    def instanciate_card(self, card_name):
        for card in self.game.current_player.hand:
            if card.name == card_name:
                return card

    def display(self, command, card=None, variation=None):
        if self.game.real:
            if command == "turn":
                print(
                    f"Turn {self.game.turn}, Player {1 if self.game.current_player == self.game.player1 else 2}'s turn"
                )
            elif command == "players_status":
                for i, player in enumerate([self.game.player1, self.game.player2]):
                    print(
                        f"Player {i+1}'s life: {player.life}, deck: {len(player.deck.cards)} cards"
                    )
            elif command == "draw_card":
                print(
                    f"Player {1 if self.game.current_player == self.game.player1 else 2} draws a card: {card.name} ({card.attack} attack, {card.cost} cost)"
                )
                print(
                    f"Player {1 if self.game.current_player == self.game.player1 else 2} plays a card: {card.name} ({card.attack} attack, {card.cost} cost)"
                )
            elif command == "current_player_hand":
                print(
                    f"Player {1 if self.game.current_player == self.game.player1 else 2}'s hand: {[i.name for i in self.game.current_player.hand]}"
                )
            elif command == "current_player_pp_change":
                print(
                    f"PP is changed {self.game.current_player.temp_pp - variation}/{self.game.current_player.max_pp} >>> {self.game.current_player.temp_pp}/{self.game.current_player.max_pp}"
                )
            elif command == "current_player_pp_update":
                print(
                    f"PP is initialized: {self.game.current_player.temp_pp}/{self.game.current_player.max_pp}"
                )
            elif command == "game":
                print(
                    f"Turn {self.game.turn}, Player {1 if self.game.current_player == self.game.player1 else 2}'s turn"
                )
                for i, player in enumerate([self.game.player1, self.game.player2]):
                    print(
                        f"Player {i+1}'s life: {player.life}, deck: {len(player.deck.cards)} cards"
                    )
                print(
                    f"Player {1 if self.game.current_player == self.game.player1 else 2}'s hand: {[i.name for i in self.game.current_player.hand]}"
                )
                print(
                    f"Player {1 if self.game.opponent_player == self.game.player1 else 2}'s hand: {[i.name for i in self.game.opponent_player.hand]}"
                )
                print(
                    f"Player {1 if self.game.opponent_player == self.game.player1 else 2}'s PP is {self.game.current_player.temp_pp}/{self.game.current_player.max_pp}"
                )


# MCTSの探索実行時に使用するGameのState
class GameStateForMCTS(TwoPlayersAbstractGameState):
    def __init__(self, game):
        self.game = game
        self.game_manager = GameManager(self.game)
        self.game.real = False
        self.next_to_move = 1 if self.game.current_player == self.game.player1 else -1

    @property
    def game_result(self):
        if self.game.winner is None:
            return None
        return 1 if self.game.winner == self.game.player1 else -1

    def is_game_over(self):
        return self.game_result is not None

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
        playable_cards = [
            card.name
            for card in self.game.current_player.hand
            if card.cost <= self.game.current_player.temp_pp
        ]
        playable_cards.append("PASS")
        return playable_cards


class MyMCTSNode(TwoPlayersGameMonteCarloTreeSearchNode):
    def __init__(self, state, parent=None):
        super().__init__(state, parent)

    def best_child(self, c_param=1.4):
        choices_weights = [
            (c.q / c.n) + c_param * np.sqrt((2 * np.log(self.n) / c.n))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def expand(self):
        action = self.untried_actions.pop()
        next_state = self.state.move(action)
        child_node = MyMCTSNode(next_state, parent=self)
        self.children.append(child_node)
        return child_node


class MyMCTS(MonteCarloTreeSearch):
    def __init__(self, node):
        super().__init__(node)
