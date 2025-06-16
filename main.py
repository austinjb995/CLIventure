#!/usr/bin/python3

import random
from enum import Enum

enemy_titles = {
    "title": ["shy", "wild", "insane", "blood hungry"]
}
enemies = [
    {"name": "goblin", "rarity": "common", "locations": ["forest", "cave"]},
    {"name": "orc", "rarity": "uncommon", "locations": ["cave", "mine"]},
    {"name": "kobold", "rarity": "common", "locations": ["mine", "cave"]},
    {"name": "beastman", "rarity": "rare", "locations": ["forest"]},
    {"name": "bandit", "rarity": "uncommon", "locations": ["swamp", "forest"]},
    {"name": "troll", "rarity": "rare", "locations": ["mine", "forest"]},
]
places = [  {"name": "cave", "description": "A damp dark cave" },
            {"name": "swamp", "description": "a murky swamp with strange noises"},
            {"name": "mine", "description":  "a mine with rich ores"},
            {"name": "forest", "description": "a lively forest with trees and bushes"},
          ]

items = [{"name": "potion", "description": "A mixture of herbal remedies, Grants 10HP", "rarity": 'uncommon', "value": 30,},
         {"name": "apple", "description": "Hey Apple!, Grants 3HP", "rarity": 'common', "value": 10,},
         {"name": "elixir", "description": "a strange concoction of herbs, Grants 1 SP, +2 blocks and +10 HP", "rarity": 'rare', "value": 100,},
         {"name": "mushroom", "description": "Far out dude..., Grants -2 SP, and 5 HP", "rarity": 'common', "value": 5,},
         ]

rarity_weights = {
     "common": 65,
     "uncommon": 20,
     "rare": 10,
     "legendary": 5,
 }
enemy_rarity_weights = {
    "common": 60,
    "uncommon": 30,
    "rare": 10,
}
class Player:
    def __init__(self, name: str, rested: bool, hp=10, sp=2, bc=0):
        self.name = name
        self.hp = hp
        self.sp = sp
        self.bc = bc
        self.rested = rested
        self.rest_count = 0
        self.scavenge_count = 0

    def attack(self, enemy):
        damage_dealt = random.randint(1, 4)
        print(f"\nYou dealt {damage_dealt} damage\n")
        enemy.receive_damage(damage_dealt)

    def receive_damage(self, damage_dealt):
        self.hp -= damage_dealt

    def death_check(self):
        if self.hp <= 0:
            print("The Brave Adventurer has met with a fatal demise.")
            exit()

    def defend(self):
        if self.bc >= 3:
            print(f"{self.name} can not defend until after a long rest!")
        else:
            self.bc += 1
            healed = random.randint(1, 4)
            self.hp += healed
            print(f"\n{self.name} healed for {healed} HP! Total HP: {self.hp}")

class Enemy:
    def __init__(self, name: str, title: str, hp=5, sp=2, bc=0, min_gold=1, max_gold=15):
        self.name = name
        self.title = title
        self.hp = hp
        self.sp = sp
        self.bc = bc
        self.apply_difficulty()
        self.min_gold = min_gold
        self.max_gold = max_gold

    def apply_difficulty(self):
        if self.title == 'wild':
            self.hp += 2
        elif self.title == 'insane':
            self.sp += 2
            self.bc -= 1
        elif self.title == 'blood hungry':
            self.hp += 5
            self.sp += 4
            self.bc -= 2

    def attack(self, player):
        damage_dealt = random.randint(1, 4)
        print(f"\nThe {self.title} {self.name} attacked you for {damage_dealt}!\n")
        player.receive_damage(damage_dealt)

    def receive_damage(self, damage_dealt):
        self.hp -= damage_dealt

    def death_check(self):
        return self.hp <= 0

    def defend_or_attack(self, player):
        d3 = random.randint(1, 3)
        d20 = random.randint(1, 20)
        if d3 == 3 and self.bc < 3:
            if d20 <= 10:
                print(f"The {self.name} tried to defend but failed!")
            else:
                self.bc += 1
                healed = random.randint(1, 4)
                self.hp += healed
                print(f"The {self.title} {self.name} defended and healed for {healed} HP! Total HP: {self.hp}")
        else:
            self.attack(player)

    def drop_gold(self):
        amount = random.randint(self.min_gold, self.max_gold)
        return amount

    @staticmethod
    def create_enemy(location=None):
        eligible_enemies = [
            e for e in enemies if location is None or location["name"] in e["locations"]
        ]
        if not eligible_enemies:
            print("No enemies found in this location. Using fallback pool")
            eligible_enemies = enemies

        weighted_enemies = []
        for e in enemies:
            weight = enemy_rarity_weights.get(e['rarity'], 1)
            weighted_enemies.extend([e] * weight)

        chosen = random.choice(weighted_enemies)
        return Enemy(
            name=chosen["name"],
            title=random.choice(enemy_titles["title"])
        )


class Inventory:
    def __init__(self):
        self.items = []
        self.gold = 0
        self.quantity = 0

    def add_gold(self, amount):
        self.gold += amount
        print(f"Added {amount} gold. Total gold: {self.gold}")

    def post_battle_drop(self):
        """
        This will calculate the probability of dropping certain items

        """
        pass
    def found_by_scavenging(self):
        weighted_items = []

     # Expand the list based on rarity weights
        for item in items:
             weight = rarity_weights.get(item['rarity'])
             weighted_items.extend([item] * weight)

        return random.choice(weighted_items)

    def add_item_to_inventory(self, item):
        self.items.append(item)
        for _ in range(1):
            print(f"You found a {item['name']}! ({item['rarity'].capitalize()}) - {item['description']}")

    def use_item(self, player):
        if not self.items:
            print("You have no items to use.")
            return

        print("Which item would you like to use?")
        for idx, item in enumerate(self.items, 1):
            print(f"{idx}. {item['name']} ({item['rarity'].capitalize()}) - {item['description']}")

        choice = input("Enter the number of the item to use (or 'c' to cancel): ")
        if choice.lower() == 'c':
            return

        try:
            index = int(choice) - 1
            if index < 0 or index >= len(self.items):
                print("Invalid choice.")
                return

            item = self.items.pop(index)  # remove item from inventory
            self.apply_item_effect(item, player)

        except ValueError:
            print("Invalid input. Please enter a number.")

    def apply_item_effect(self, item, player):
        name = item['name'].lower()
        if name == "potion":
            player.hp += 10
            print("\nYou feel better. +10 HP!")
        elif name == "apple":
            player.hp += 3
            print("\nCrisp and sweet. +3 HP!")
        elif name == "elixir":
            player.sp += 1
            player.bc += 2
            player.hp += 10
            print("\nStrange energy courses through you. +10 HP +1 SP, +2 Block Chance!")
        elif name == "mushroom":
            player.hp += 5
            player.sp -= 2
            print("\nThat tasted weird... +5 HP, -2 SP")
        else:
            print("Nothing happened...")

class Place:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @staticmethod
    def generate_location():
       place = random.choice(places)
       return place

def post_battle(player, victories):
    print(f"Number of battles won: {victories}")
    print("After a Long Battle, the Brave Adventurer settles down...\n")

    while True:
        selection = input("\nMake a choice (1)-Rest (2)-Battle (3)-Scavenge (4)-View Stats (5)-View Inventory (6)-Use Item: ")
        if selection == "1":
            if player.rested == True:
                print(f"{player.name} is already well rested!")
            elif not player.rested and player.rest_count == 0:
                print("\nYou feel well rested...\n")
                player.bc = 0
                player.hp += 5
                print(f"{player.name} gained 5 HP\n")
                player.rest_count += 1
                player.scavenge_count = 0
                player.rested = True
            else:
                print(f"{player.name} yearns for battle!")
        elif selection == "2":
            enemy = Enemy.create_enemy()
            print(f"\nYou have encountered a {enemy.title} {enemy.name} (HP: {enemy.hp}, SP: {enemy.sp})")
            player.rest_count = 0
            player.rested = False
            return enemy
        elif selection == "3":
                if not player.rested:
                    print("\nYou are too tired to scavenge again. You must rest!")
                elif player.rested == True and player.scavenge_count <= 3:

                   # location = Place.generate_location()
                   # print(f"\nYou came across a {location['name']}\n{location['description']}")
                    item = inventory.found_by_scavenging()
                    inventory.add_item_to_inventory(item)
                    player.scavenge_count += 1
                elif player.scavenge_count >= 3 and not player.rested:
                    print(f"\n{player.name} is too tired to scavenge...")
                elif player.rested and player.scavenge_count < 3 or player.scavenge_count > 3:
                    print(f"\n{player.name} found nothing of importance...")

        elif selection == "4":
            print(f"\nHP: {player.hp}\nSP: {player.sp}\nBC: {player.bc}\n Rest Status: {player.rested}")

        elif selection == "5":
            if not inventory.items:
                print("\nYour inventory is empty.\n")

            print("\nInventory:")
            print("-" * 40)
            for idx, item in enumerate(inventory.items, 1):
                name = item.get("name", "Unknown Item")
                desc = item.get("description", "")
                rarity = item.get("rarity", "common").capitalize()
                value = item.get("value", 0)
                print(f"{idx}. {name} ({rarity})")
                print(f"   {desc}")
                print(f"   Value: {value}g")
                print("-" * 40)
            print(f"Total Gold: {inventory.gold}")
        elif selection == "6":
            inventory.use_item(player)
        else:
            print("Incorrect Input")


def turn_order(player, enemy):
    d3 = random.randint(1, 3)
    d20 = random.randint(1, 20)

    if player.sp > enemy.sp:
        player.attack(enemy)
        if enemy.death_check():
            print(f"You have slain the {enemy.title} {enemy.name}!")
            player.rested = False
            return True
        enemy.defend_or_attack(player)
        player.death_check()
    elif enemy.sp > player.sp:
        enemy.defend_or_attack(player)
        player.death_check()
        player.attack(enemy)
        if enemy.death_check():
            print(f"You have slain the {enemy.title} {enemy.name}!")
            player.rested == False
            return True
    else:
        # Speed tie
        player_roll = random.randint(1, 20)
        enemy_roll = random.randint(1, 20)
        if player_roll >= enemy_roll:
            player.attack(enemy)
            if enemy.death_check():
                print(f"You have slain the {enemy.title} {enemy.name}!")
                player.rested == False
                return True
            enemy.defend_or_attack(player)
            player.death_check()
        else:
            enemy.defend_or_attack(player)
            player.death_check()
            player.attack(enemy)
            if enemy.death_check():
                print(f"You have slain the {enemy.title} {enemy.name}!")
                player.rested == False
                return True
    return False


# Game Initialization
name = input("Name your adventurer: ")

player = Player(name, False)
inventory = Inventory()
enemy = Enemy.create_enemy()
victories = 0

print(f"\nBrave Adventurer {player.name} has set forth on an adventure\n")
print(f"The Brave Adventurer encountered a {enemy.title} {enemy.name} (HP: {enemy.hp})")

# Main Game Loop
while True:
    selection = input(f"\nMake a choice (1)-Attack (2)-Defend (3)-View Stats (4)-Use Item: ")
    if selection == "1":
        victory = turn_order(player, enemy)
        if victory:
            victories += 1
            amount = Enemy.drop_gold(enemy)
            inventory.add_gold(amount)
            enemy = post_battle(player, victories)
    elif selection == "2":
        player.defend()
        enemy.defend_or_attack(player)
        player.death_check()
    elif selection == "3":
        print(f"\nPlayer HP: {player.hp}")
        print(f"Player SP: {player.sp}")
        print(f"Player BC: {player.bc}\n")
        print(f"Enemy HP: {enemy.hp}")
        print(f"Enemy SP: {enemy.sp}")
        print(f"Enemy BC: {enemy.bc}\n")
    elif selection == '4':
        inventory.use_item(player)
        if len(inventory.items) > 0:
            enemy.defend_or_attack(player)
        player.death_check()
    else:
        print("Incorrect input")
