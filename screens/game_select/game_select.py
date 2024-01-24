from misc.ui import *
from misc.constants import *
from screens.screen import Screen

class Game_select(Screen):
    def __init__(self, screen_manager) -> None:
        super().__init__(screen_manager)
        self.back_color = (DARK_BACKGROUND_COLOR)

        # btn_start
        self.add_item("btn_play",Button(BUTTON_DARK , rect=(50,85,180,100), text="PLAY", positioning="relative", on_click= self.btn_heroes_on_click))
        self.add_item("btn_heroes",Button(BUTTON_DARK , rect=(30,87,270,100), text="HEROES", positioning="relative", on_click= self.btn_heroes_on_click))
        self.add_item("btn_upgrades",Button(BUTTON_DARK , rect=(70,87,270,100), text="UPGRADE", positioning="relative", on_click= self.btn_heroes_on_click))
        
        for item in self.items:
            self.add_animation(f"{item}_open", [self.items[item].rect.x, self.items[item].rect.y + 250, self.items[item].rect.width, self.items[item].rect.height], self.items[item].rect, 20, self.items[item], "rect")
            self.add_animation(f"{item}_close",self.items[item].rect, [self.items[item].rect.x, self.items[item].rect.y + 250, self.items[item].rect.width, self.items[item].rect.height], 20, self.items[item], "rect")
        #btn_back
        self.add_item("btn_back", Button(BUTTON_DARK_NO_FILL , rect = (25,25,50,50), text = "X", on_click= self.btn_back_on_click))

        #btn_settings
        self.add_item("btn_settings", Button(BUTTON_DARK, rect = (97,5,50,50), text = "{o}", positioning="relative", on_click= self.btn_settings_on_click))
        self.add_animation("btn_settings_open", [self.items["btn_settings"].rect.x + 100, self.items["btn_settings"].rect.y , self.items["btn_settings"].rect.width, self.items["btn_settings"].rect.height], self.items["btn_settings"].rect, 20, self.items["btn_settings"], "rect")
        self.add_animation("btn_settings_close",self.items["btn_settings"].rect, [self.items["btn_settings"].rect.x + 100, self.items["btn_settings"].rect.y , self.items["btn_settings"].rect.width, self.items["btn_settings"].rect.height], 20, self.items["btn_settings"], "rect")

        self.add_item("lbl_title", Label(LABEL_DARK, rect = (50,40,SCREEN_WIDTH,200), text = "TOWER DEFENCE", positioning="relative", font_size=100))

        

    def on_open(self):
        self.animations["btn_play_open"][0].start_animation()
        self.animations["btn_heroes_open"][0].start_animation()
        self.animations["btn_upgrades_open"][0].start_animation()
        self.animations["btn_settings_open"][0].start_animation()

    def on_close(self):
        for animation in self.animations:
            if animation[-5:] == "close":
                self.animations[animation][0].start_animation()

    def btn_back_on_click(self):
        self.screen_manager.change_screen("menu", 20)
        
    def btn_heroes_on_click(self):
        self.screen_manager.change_screen("heroes", 20)

    def btn_settings_on_click(self):
        self.screen_manager.change_screen("settings", 20)