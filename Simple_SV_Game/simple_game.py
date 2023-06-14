import json
import random

from card_entity import Card
from deck_structure import Deck
from game_environment import Game, GameManager


def create_template_deck(cards_data):
    deck_cards = []
    # template_deck: card1:10, card2:10
    for card_data in cards_data:
        for _ in range(10):
            deck_cards.append(
                Card(card_data["name"], card_data["attack"], card_data["cost"])
            )
    random.shuffle(deck_cards)
    return Deck(deck_cards)


def main():
    json_file = "cards.json"
    with open(json_file, "r") as f:
        cards_data = json.load(f)["cards"]

    print("Select operation mode:")
    print("1: Auto mode")
    print("2: Player mode")
    mode = input("Enter the number of the mode: ")

    template_deck1 = create_template_deck(cards_data)
    template_deck2 = create_template_deck(cards_data)
    decks = [template_deck1, template_deck2]

    game = Game(decks=decks, mode=mode)
    game.setup_game()
    game_manager = GameManager(game)
    while True:
        if game_manager.AutoGameStep():
            break
    game_manager.game.end_game()


if __name__ == "__main__":
    main()
