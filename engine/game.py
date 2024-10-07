import pygame
import sys
import os 

from game.level import Generator
from .sound import SoundManager
from .entity import EntityManager
from .screen_manager import *
from .screen import Screen
from screens import *
from .ui import *

from entities import *

screens = {
    "menu": Menu,
    "game_select": Game_select, 
    "settings": Settings,
    "heroes": Heroes,
    "upgrades": Upgrades
    }

class Assets: 
    def __init__(self) -> None:
        self.assets = {}
        self.load()
    
    def load(self):
        for file in os.scandir("assets/images"):
            if file.is_dir():
                for file in os.scandir(file.path):
                    if file.name.split(".")[-1] == "png":
                        self.assets[file.name.split(".")[0]] = pygame.image.load(file.path)
                        self.assets[file.name.split(".")[0]].set_colorkey((0,0,0))
            if file.name.split(".")[-1] == "png":
                self.assets[file.name.split(".")[0]] = pygame.image.load(file.path)
                self.assets[file.name.split(".")[0]].set_colorkey((0,0,0))

    def get(self, key):
        return self.assets.get(key, self.assets["null"])


class Engine:
    def __init__(self, screens):
        self.config, self.keybinds = self.load_config()
        self.running = True
        
        # setup the display
        self.screen = pygame.display.set_mode((int(self.config.get("SCREEN_WIDTH")), int(self.config.get("SCREEN_HEIGHT"))))

        # get all the managers in one place finally thank god
        self.sound_manager = SoundManager(self)
        self.entity_manager = EntityManager()
        self.screen_manager = ScreenManager(self, "menu", screens)
        
        self.clock = pygame.time.Clock()

    def run(self):
        while self.running:
            self.check_events()
            self.draw()
            self.update()
            self.clock.tick(60)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.quit()
                self.running = False

    def update(self):
        self.screen_manager.update()

    def draw(self):
        self.screen.fill((0,0,0))
        self.screen_manager.draw()
        pygame.display.flip()
        
        
    def load_config(self):
        config = {}
        keybinds = {}
        with open("config.cfg") as fconfig:
            for line in fconfig.readlines():
                split = line.split(" ")
                if line[0] != "#" and len(split) > 1:
                    if split[0].upper() == "BIND":
                        keybinds[split[2].strip("\n")] = pygame.key.key_code(split[1])
                        continue
                    config[split[0]] = split[1].strip("\n")
        return config, keybinds

class Game(Engine):
    def __init__(self):
        super().__init__(screens)
        # assets
        self.assets = Assets()

        # holds whether or not the game screen is open
        self.game_active = False

        # holds game state information
        self.paused = False
        self.game_speed = 1.0

        # the information needed for the current round 
        self.round_started = False
        self.enemy_types = {
            "standard": {
                "type": Standard,
                "chance": 100,
                "sprite": self.assets.get("enemy")
                },
            "fast": {
                "type": Fast,
                "chance": 50,
                "sprite": self.assets.get("enemy")
                }
            }
        self.current_round = Round(self, 0,self.enemy_types)

        # popups
        self.popups = {
            "pause": Pause(self)
        }

        # setup GUI
        self.gui = Screen(self.screen_manager)
        self.gui.add_item("lbl_fps", Label(LABEL_DARK, rect = (98, 98, 125, 50), text = self.get_fps, font_size=20, positioning="relative"))
        self.gui.add_item("lbl_round", Label(LABEL_DARK, rect = (98, 2, 125, 50), text = self.get_round_number, font_size=30, positioning="relative"))
        self.gui.add_item("btn_roundstart", Button(BUTTON_DARK , rect = (95,90,100,100), text = get_icon_hex("play_arrow"), on_click= self.start_round, positioning="relative"))
        self.gui.add_item("btn_fastforward", Button(BUTTON_DARK , rect = (95,90,100,100), text = get_icon_hex("fast_forward"), on_click= self.fast_forward, positioning="relative"))
        self.gui.items["btn_fastforward"].hidden = True

        self.screen_manager.add_screen("game", self.gui)
        
        # level data / generation
        self.level_data = {
            "no_turns": 6,
            "no_boxes": 6,
            "max_line_len": 1000
            }
        self.generator = Generator(self.screen.get_size())
        self.level = self.generator.generate_level(self.level_data)
        
        # setup draw and update queues
        self.draw_queue = []
        self.update_queue = []

        # add the level and entity manager to the draw queue
        self.draw_queue.append((1, self.level))
        self.draw_queue.append((2, self.entity_manager))
        self.draw_queue.append((6, self.screen_manager))
        self.update_queue.append(self.entity_manager)
        self.update_queue.append(self.screen_manager)
        self.update_queue.append(self.current_round)

        self.entity_manager.add_entity(Player(self,"player"),"player")
        tower = Tower(self, pygame.Vector2(SCREEN_WIDTH / 2, 0))
        tower.velocity = pygame.Vector2(0,random.randrange(8,15))
        tower.velocity.rotate_ip(random.randrange(-45,45))
        self.entity_manager.add_entity(tower, "tower")


    def draw(self):
        if self.game_active:
            self.draw_queue.sort()
            for item in self.draw_queue:
                if self.paused and item[1] == self.screen_manager:
                    item[1].draw()
                    pygame.display.flip()
                    break
                item[1].draw()
            pygame.display.flip()
        else:
            super().draw()

    def update(self):
        self.game_active = self.screen_manager.current_screen == "game"
        if self.game_active:
            if pygame.key.get_just_pressed()[self.keybinds.get("pause", -1)]:
                self.toggle_popup(self.popups["pause"])
            if self.paused:
                for item in self.update_queue:
                    if item == self.screen_manager:
                        item.update()
                return
            for item in self.update_queue:
                item.update()
                if self.game_speed == 2.0:
                    item.update()
        else:
            super().update()

    def get_fps(self):
        return int(self.clock.get_fps())

    def get_round_number(self):
        return self.current_round.get_round_number()
    
    def start_round(self):
        self.gui.items["btn_roundstart"].hidden = True
        self.gui.items["btn_fastforward"].hidden = False
        self.update_queue.remove(self.current_round)
        self.current_round = Round(self, self.current_round.get_round_number()+1, self.enemy_types)
        self.update_queue.append(self.current_round)
        self.round_started = True
        self.fast_forward()

    def fast_forward(self):
        btn = self.gui.items["btn_fastforward"]
        if self.game_speed == 2.0:
            self.game_speed = 1.0
            btn.border_color = DARK_ACCENT_COLOR
            btn.border_width = 2 
            btn.hover_color = btn.theme.get()["hover_color"]
            btn.fore_color = DARK_ACCENT_COLOR
        else:
            self.game_speed = 2.0
            btn.color = btn.theme.get()["color"]
            btn.border_color = btn.theme.get()["fore_color"]
            btn.border_width = 2 
            btn.hover_color = btn.theme.get()["hover_color"]
            btn.fore_color = btn.theme.get()["fore_color"]


    def toggle_popup(self, popup):
        if popup.name in self.gui.items:
            popup.on_close()
            self.gui.remove_item(popup.name)
        else:
            self.gui.add_item(popup.name, popup)
            popup.on_open()

class Pause(Popup):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.name = "pause"
        self.add_item(Rect(RECT_DARK, (50, 50, 500, 500), positioning="relative"))
        self.add_item(Label(LABEL_DARK, (50, 8, 1000, 100), text= "PAUSED", positioning="relative", font_size=80))
        self.add_item(Button(BUTTON_DARK, (50, 51, 400, 100), text="SETTINGS", on_click=self.game.screen_manager.change_screen, click_args=["settings", 1], positioning="relative"))
        self.add_item(Button(BUTTON_DARK, (50, 28, 400, 100), text="CONTINUE", on_click=self.game.toggle_popup, click_args=[self], positioning="relative"))
        self.add_item(Button(BUTTON_DARK, (50, 73, 400, 100), text="EXIT", on_click=self.game.screen_manager.change_screen, click_args=["game_select", 1], positioning="relative"))
    
    def on_close(self):
        self.game.paused = False

    def on_open(self):
        self.game.paused = True

class UpgradePopup(Popup):
    def __init__(self, game):
        super().__init__(game)

class Round:
    def __init__(self, game, round_number, enemy_types):
        self.game = game
        self.round_number = round_number
        self.number_enemies = int(round_number ** 1.2)
        self.enemies = []
        self.enemy_delay = 60
        self.counter = 1000 
        for i in range(self.number_enemies):
            for enemy_type in enemy_types:
                for _ in range(self.number_enemies * enemy_types[enemy_type]["chance"] // 100):
                    self.enemies.append(enemy_types[enemy_type]["type"](game, sprite = enemy_types[enemy_type]["sprite"]))

    def get_round_number(self):
        return self.round_number

    def update(self):
        self.counter += 1 
        if self.game.round_started:
            if len(self.enemies) > 0 and self.counter >= self.enemy_delay:
                self.counter = 0
                enemy = random.choice(self.enemies)
                self.game.entity_manager.add_entity(enemy, "enemy")
                self.enemies.remove(enemy)
            if len(self.game.entity_manager.entities.get("enemy", [])) == 0:
                self.game.round_started = False
                self.game.gui.items["btn_roundstart"].hidden = False
                self.game.gui.items["btn_fastforward"].hidden = True
                self.game.game_speed = 1.0