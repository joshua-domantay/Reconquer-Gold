# Made by Joshua Anthony Domantay
# Version 1.0
# 17/04/2019
import pygame as pg
from os import path
from settings import *
from sprites import *


def draw_text(screen, text, color, size, position, coordinates):
    font = pg.font.Font(path.abspath("assets/fonts/slkscrb.ttf"), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if (position == "center"):
        text_rect.center = coordinates
    else:
        text_rect.topleft = coordinates
    screen.blit(text_surface, text_rect)

def draw_hp(sprite, screen, x, y, width, height, color):
    if (sprite.current_hp <= 0):
        sprite.current_hp = 0
    fill = (sprite.current_hp / sprite.original_hp) * width
    outline_rect = pg.Rect(x, y, width, height)
    fill_rect = pg.Rect(x, y, fill, height)
    pg.draw.rect(screen, color, fill_rect)
    pg.draw.rect(screen, COLOR_WHITE, outline_rect, 1)


class Game():
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        pg.display.set_caption(GAME_TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    # Game booleans and sprite groups
    def load_data(self):
        self.level = 1
        self.win_text_delay = 0
        self.last_spawn = 0
        self.current_comic = 0
        self.running = True
        self.playing = False
        self.pause = False
        self.waiting = False
        self.spawning = False
        self.game_won = False
        self.play_again = False
        self.current_screen = "main"

        self.mouse_btn1_pressed = False  # Prevents losing a coin before game starts
        self.mouse_btn3_pressed = False  # Prevents buying health more than once

        self.grp_allSprites = pg.sprite.Group()
        self.grp_buttons = pg.sprite.Group()
        self.grp_mobs = pg.sprite.Group()
        self.grp_walls = pg.sprite.Group()
        self.grp_playerBullets = pg.sprite.Group()
        self.grp_mobBullets = pg.sprite.Group()
        self.grp_mobLasers = pg.sprite.Group()

        # Load assets
        self.folder_main = path.dirname(__file__)
        self.folder_assets = path.join(self.folder_main, "assets")
        self.folder_imgs = path.join(self.folder_assets, "imgs")
        self.folder_snds = path.join(self.folder_assets, "snds")
        self.folder_comics = path.join(self.folder_imgs, "comics")

        # Images
        self.spritesheet = Spritesheet(path.join(self.folder_imgs, "img_spritesheet.png"))
        self.img_game_background = pg.image.load(path.join(self.folder_imgs, "img_game_background.png")).convert()
        self.img_train_background = pg.image.load(path.join(self.folder_imgs, "img_train_background.png")).convert()
        self.img_train_background.set_colorkey(COLOR_GREEN)
        self.img_main_background = pg.image.load(path.join(self.folder_imgs, "img_main_background.png")).convert()
        self.img_htp_background = pg.image.load(path.join(self.folder_imgs, "img_htp_background.png")).convert()
        self.img_htp_menu = pg.image.load(path.join(self.folder_imgs, "img_htp_menu.png")).convert()
        self.img_pause_menu = pg.image.load(path.join(self.folder_imgs, "img_pause_menu.png")).convert()
        self.img_ground = pg.image.load(path.join(self.folder_imgs, "img_ground.png")).convert()
        self.img_shop = self.spritesheet.get_image(72, 112, 148, 108)
        self.img_player = self.spritesheet.get_image(0, 234, 16, 78)
        self.img_player_gun = self.spritesheet.get_image(16, 234, 84, 84)
        self.img_player_bullet = self.spritesheet.get_image(96, 224, 8, 8)
        self.img_mob_boss_gun = self.spritesheet.get_image(324, 136, 42, 42)
        self.img_head = self.spritesheet.get_image(220, 112, 32, 34)
        self.img_head_bullet = self.spritesheet.get_image(252, 112, 18, 4)
        self.img_guard_gun = self.spritesheet.get_image(100, 234, 84, 84)
        self.img_guard_board = self.spritesheet.get_image(0, 224, 96, 10)
        self.img_rotor_main = self.spritesheet.get_image(220, 236, 90, 90)
        self.img_rotor_body = self.spritesheet.get_image(220, 146, 90, 90)
        self.img_rotor_bullet = self.spritesheet.get_image(77, 335, 15, 15)
        self.img_white_circle = self.spritesheet.get_image(366, 136, 100, 100)
        # Comics
        self.comics = []
        for i in range(1, 18):
            img = pg.image.load(path.join(self.folder_comics, "comic{}.png".format(i))).convert()
            self.comics.append(img)

        # Sounds
        self.msc_train_tracks = pg.mixer.Sound(path.join(self.folder_snds, "msc_train_tracks.wav"))
        self.snd_bullet_coin = pg.mixer.Sound(path.join(self.folder_snds, "snd_bullet_coin.wav"))
        self.snd_hp = pg.mixer.Sound(path.join(self.folder_snds, "snd_hp.wav"))
        self.snd_mob_dead = pg.mixer.Sound(path.join(self.folder_snds, "snd_mob_dead.wav"))
        self.snd_mob_head = pg.mixer.Sound(path.join(self.folder_snds, "snd_mob_head.wav"))
        self.snd_mob_rotor = pg.mixer.Sound(path.join(self.folder_snds, "snd_mob_rotor.wav"))
        self.snd_player_hit = pg.mixer.Sound(path.join(self.folder_snds, "snd_player_hit.wav"))

    # Loads game sprites
    def reset(self):
        self.spawnNumber = 0
        self.spawnNow = False
        self.current_comic = 0
        self.win_text_delay = 0
        self.level = 9
        self.last_spawn = pg.time.get_ticks()
        self.spawning = True
        self.pause = False
        self.game_won = False

        self.img_white_circle = self.spritesheet.get_image(366, 136, 100, 100)

        # Shop
        self.shop = Shop(self, (GAME_WIDTH / 2), GAME_HEIGHT - (GAME_TILESIZE * 2.5))

        # Walls
        self.ground = Wall(self, "ground", 0, GAME_HEIGHT - (GAME_TILESIZE * 2.5), GAME_WIDTH, GAME_TILESIZE * 2.5)
        Wall(self, "floating", 0, GAME_HEIGHT - GAME_TILESIZE * 7, GAME_TILESIZE * 6, 1)
        Wall(self, "floating", GAME_WIDTH - GAME_TILESIZE * 6, GAME_HEIGHT - GAME_TILESIZE * 7, GAME_TILESIZE * 6, 1)

        # Backgrounds
        self.game_ground = ExtraGraphics(self.ground, self, "game_ground", "bottomleft", 0, GAME_HEIGHT)
        self.game_background = ExtraGraphics(self.ground, self, "game_background", "bottomleft", 0, GAME_HEIGHT)

        # Player
        self.player = Player(self, 40, (GAME_HEIGHT - GAME_TILESIZE * 3))

    def spawnDelay(self, delay):
        now = pg.time.get_ticks()
        # (now - self.last_spawn) >= (first_delay + second_delay + ... + current_delay)
        if (((now - self.last_spawn) >= delay) and ((now - self.last_spawn) <= (delay + 100))):
            self.last_spawn -= 100
            return True
        else:
            return False

    # Spawns mobs for each level
    def checkLevel(self):
        now = pg.time.get_ticks()

        if (self.spawning):
            if (self.level == 1):
                if (self.spawnDelay(0)):
                    spawnMob(self, "head", "right")
                if (self.spawnNow):
                    if (self.spawnNumber == 1):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l, h-r")
                        spawnMob(self, "head", "left")
                    elif (self.spawnNumber == 2):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l")
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                    elif (self.spawnNumber == 3):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: None")
                        spawnMob(self, "guard", "left")
                        print("last\n")
                        self.spawning = False  # End level
                        self.spawnNumber = 0
                    self.spawnNow = False
            elif (self.level == 2):
                if (self.spawnDelay(0)):
                    spawnMob(self, "head", "left")
                    spawnMob(self, "guard", "left")
                    print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-r")
                if (self.spawnNow):
                    if (self.spawnNumber == 1):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-l")
                        spawnMob(self, "guard", "right")
                    if (self.spawnNumber == 2):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-r")
                        spawnMob(self, "rotor", "left")
                    if (self.spawnNumber == 3):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l, g-r")
                        spawnMob(self, "head", "right")
                    if (self.spawnNumber == 4):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-r")
                        spawnMob(self, "head", "left")
                        spawnMob(self, "guard", "right")
                    if (self.spawnNumber == 5):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l")
                        spawnMob(self, "head", "right")
                    if (self.spawnNumber == 6):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-r")
                        spawnMob(self, "head", "left")
                    if (self.spawnNumber == 7):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: l-l")
                        spawnMob(self, "head", "right")
                    if (self.spawnNumber == 8):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: l-r")
                        spawnMob(self, "laser", "left")
                    if (self.spawnNumber == 9):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: none")
                        spawnMob(self, "laser", "right")
                        self.spawnNumber = 0
                        self.spawning = False  # End level
                    self.spawnNow = False
            elif (self.level == 3):
                if (self.spawnDelay(0)):
                    spawnMob(self, "head", "left")
                    spawnMob(self, "guard", "right")
                    print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-r, h-r")
                if (self.spawnNow):
                    if (self.spawnNumber == 1):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-l")
                        spawnMob(self, "rotor", "right")
                        spawnMob(self, "head", "right")
                    if (self.spawnNumber == 2):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l, g-r")
                        spawnMob(self, "rotor", "left")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 3):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l, h-r")
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "guard", "right")
                    if (self.spawnNumber == 4):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-r, r-r")
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                    if (self.spawnNumber == 5):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: None")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "rotor", "right")
                        self.spawnLaserMob()
                        self.spawnNumber = 0
                        # Up to 280000
                        self.spawning = False  # End level
                    self.spawnNow = False
            elif (self.level == 4):
                if (self.spawnDelay(0)):
                    print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l")
                    spawnMob(self, "rotor", "right")
                    spawnMob(self, "head", "left")
                    self.spawnLaserMob()
                if (self.spawnNow):
                    if (self.spawnNumber == 1):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-b")
                        spawnMob(self, "guard", "left")
                    if (self.spawnNumber == 2):
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-r")
                    if (self.spawnNumber == 3):
                        spawnMob(self, "head", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l, g-r")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 4):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-l, h-r")
                        spawnMob(self, "head", "left")
                        spawnMob(self, "guard", "right")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 5):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l, g-r")
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "head", "right")
                    if (self.spawnNumber == 6):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-r, h-l")
                        spawnMob(self, "head", "left")
                        spawnMob(self, "guard", "right")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 7):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: None")
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        self.spawnLaserMob()
                        self.spawnNumber = 0
                        self.spawning = False  # End level
                    self.spawnNow = False
            elif (self.level == 5):
                if (self.spawnDelay(0)):
                    spawnMob(self, "rotor", "left")
                    spawnMob(self, "guard", "left")
                    spawnMob(self, "guard", "right")
                    print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l")
                    self.spawnLaserMob()
                if (self.spawnNow):
                    if (self.spawnNumber == 1):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-r, h-r, r-r")
                        spawnMob(self, "head", "left")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 2):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l, h-r")
                        spawnMob(self, "guard", "right")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "rotor", "right")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 3):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-l, r-r, g-l")
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                    if (self.spawnNumber == 4):
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        spawnMob(self, "guard", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 5):
                        spawnMob(self, "head", "left")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b, g-l")
                    if (self.spawnNumber == 6):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "guard", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-b, h-l")
                    if (self.spawnNumber == 7):
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        spawnMob(self, "head", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b")
                    if (self.spawnNumber == 8):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l, r-b")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 9):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: None")
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        self.spawnNumber = 0
                        self.spawning = False  # End level
                    self.spawnNow = False
            elif (self.level == 6):
                if (self.spawnDelay(0)):
                    spawnMob(self, "head", "left")
                    spawnMob(self, "head", "right")
                    spawnMob(self, "rotor", "left")
                    print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l")
                    self.spawnLaserMob()
                if (self.spawnNow):
                    if (self.spawnNumber == 1):
                        spawnMob(self, "guard", "left")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-r, h-l")
                    if (self.spawnNumber == 2):
                        spawnMob(self, "guard", "right")
                        spawnMob(self, "head", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-r")
                    if (self.spawnNumber == 3):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l, h-r")
                        spawnMob(self, "rotor", "right")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 4):
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "head", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b, r-r")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 5):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "rotor", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b, r-r, g-l")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 6):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "rotor", "right")
                        spawnMob(self, "guard", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: random laser")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 7):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 8):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l, r-l")
                    if (self.spawnNumber == 9):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "rotor", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-r")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 10):
                        spawnMob(self, "rotor", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-r, r-b")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 11):
                        spawnMob(self, "guard", "right")
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: none")
                        # Up to 220000
                        self.spawnNumber = 0
                        self.spawning = False  # End level
                    self.spawnNow = False
            elif (self.level == 7):
                if (self.spawnDelay(0)):
                    spawnMob(self, "guard", "left")
                    spawnMob(self, "guard", "right")
                    spawnMob(self, "rotor", "left")
                    spawnMob(self, "rotor", "right")
                    print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b")
                if (self.spawnNow):
                    if (self.spawnNumber == 1):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-r, h-l")
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 2):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l, g-r")
                        spawnMob(self, "rotor", "right")
                        spawnMob(self, "head", "left")
                    if (self.spawnNumber == 3):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b")
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "guard", "right")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 4):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-b, h-l")
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 5):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l, g-r")
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        spawnMob(self, "head", "left")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 6):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l, h-r")
                        spawnMob(self, "head", "left")
                        spawnMob(self, "guard", "right")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 7):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b, g-l")
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "head", "right")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 8):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "guard", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-r, r-l")
                    if (self.spawnNumber == 9):
                        spawnMob(self, "guard", "right")
                        spawnMob(self, "rotor", "left")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-b, r-b")
                    if (self.spawnNumber == 10):
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "guard", "right")
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l")
                    if (self.spawnNumber == 11):
                        spawnMob(self, "head", "left")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-r")
                    if (self.spawnNumber == 12):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: none")
                        spawnMob(self, "head", "right")
                        self.spawnLaserMob()
                        # Up to 320000
                        self.spawnNumber = 0
                        self.spawning = False  # End level
                    self.spawnNow = False
            elif (self.level == 8):
                if (self.spawnDelay(0)):
                    spawnMob(self, "head", "left")
                    spawnMob(self, "head", "right")
                    spawnMob(self, "guard", "left")
                    spawnMob(self, "guard", "right")
                    print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-b")
                    self.spawnLaserMob()
                if (self.spawnNow):
                    if (self.spawnNumber == 1):
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b")
                    if (self.spawnNumber == 2):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l, g-l, r-l")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 3):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "rotor", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l, r-b")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 4):
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b, g-r")
                    if (self.spawnNumber == 5):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "guard", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 6):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b, r-b")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 7):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b, g-l")
                    if (self.spawnNumber == 8):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "guard", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b")
                    if (self.spawnNumber == 9):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-l")
                    if (self.spawnNumber == 10):
                        spawnMob(self, "rotor", "left")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-r, h-l")
                    if (self.spawnNumber == 11):
                        spawnMob(self, "guard", "right")
                        spawnMob(self, "head", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-b, g-l, h-r")
                    if (self.spawnNumber == 12):
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "head", "right")
                        self.spawnNumber = 0

                        # Up to 150000
                        self.spawning = False  # End level
                    self.spawnNow = False
            elif (self.level == 9):
                if (self.spawnDelay(0)):
                    spawnMob(self, "head", "left")
                    print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-r")
                if (self.spawnNow):
                    if (self.spawnNumber == 1):
                        spawnMob(self, "head", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 2):
                        spawnMob(self, "head", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-r")
                    if (self.spawnNumber == 3):
                        spawnMob(self, "rotor", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l")
                    if (self.spawnNumber == 4):
                        spawnMob(self, "guard", "left")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b")
                    if (self.spawnNumber == 5):
                        spawnMob(self, "head", "right")
                        spawnMob(self, "head", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-r")
                    if (self.spawnNumber == 6):
                        spawnMob(self, "guard", "right")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-l, g-l")
                    if (self.spawnNumber == 7):
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "guard", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-b, r-l")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 8):
                        spawnMob(self, "head", "left")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "rotor", "left")
                        self.spawnLaserMob()
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-l, r-r")
                    if (self.spawnNumber == 9):
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "rotor", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-r, h-l")
                    if (self.spawnNumber == 10):
                        spawnMob(self, "guard", "right")
                        spawnMob(self, "head", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: g-b")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 11):
                        spawnMob(self, "guard", "left")
                        spawnMob(self, "guard", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-l")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 12):
                        spawnMob(self, "head", "left")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: r-l, h-r")
                        self.spawnLaserMob()
                    if (self.spawnNumber == 13):
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "head", "right")
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: h-r, r-b, g-l")
                    if (self.spawnNumber == 14):
                        print(str(self.spawnNumber) + "\t" + str(now - self.last_spawn) + "\t" + "next: spawnLaserRandom")
                        spawnMob(self, "head", "right")
                        spawnMob(self, "rotor", "left")
                        spawnMob(self, "rotor", "right")
                        spawnMob(self, "guard", "left")
                    if (self.spawnNumber == 15):
                        self.spawnLaserMob()
                        self.spawnNumber = 0

                        self.spawning = False  # End level
                    self.spawnNow = False
            elif (self.level == 10):
                self.boss = MobBoss(self, GAME_WIDTH / 2, -GAME_TILESIZE * 4)
                self.boss.last_shot_lasers = now
                self.spawning = False
        else:
            self.last_spawn = now

    # Spawn lAaser mob randomly
    def spawnLaserMob(self):
        random_int = random.randrange(5)
        if (random_int == 1):
            random_int = random.randrange(2)
            if (random_int == 1):
                spawnMob(self, "laser", "left")
            else:
                spawnMob(self, "laser", "right")

    # Deletes every sprite in a sprite group
    def kill_group(self, spriteGroup):
        for sprite in spriteGroup:
            sprite.killSelf()

    # Game loop
    def run(self):
        if (not self.play_again):
            self.current_screen = "comic"
            self.current_comic = 0
            self.show_screens()
            self.current_screen = "main"
        else:
            self.play_again = False
        self.reset()

        # Game loop
        self.msc_train_tracks.play(-1)
        self.mouse_btn3_pressed = False
        while self.playing:
            self.dt = self.clock.tick(GAME_FPS) / 1000
            self.events()
            self.update()
            self.draw()
        self.msc_train_tracks.stop()

        self.kill_group(self.grp_allSprites)
        if (self.player.current_hp <= 0):
            self.current_screen = "game_over"
            self.show_screens()
        elif (self.level >= 10):
            if (self.boss.current_hp <= 0):
                self.current_screen = "win"
                self.win_text_delay = pg.time.get_ticks()
                self.show_screens()

    # Updates every sprite
    def update(self):
        if (not self.pause):
            if (self.player.current_hp <= 0):
                self.playing = False

            self.checkLevel()

            self.grp_allSprites.update()
            self.game_background.update()
        else:
            self.grp_buttons.update()

    # Update screens
    def update_screens(self):
        self.grp_allSprites.update()

        if (self.current_screen == "main"):
            for bullet in self.grp_playerBullets:
                # Play rect
                rect = pg.Rect(552, 40, 112, 112)
                hits = rect.colliderect(bullet.rect)
                if (hits):
                    self.playing = True
                    self.current_screen = "main"
                    self.waiting = False
                # How to play rect
                rect = pg.Rect(496, 184, 112, 112)
                hits = rect.colliderect(bullet.rect)
                if (hits):
                    self.playing = False
                    self.current_screen = "htp"
                    self.waiting = False
                # Quit rect
                rect = pg.Rect(560, 344, 112, 104)
                hits = rect.colliderect(bullet.rect)
                if (hits):
                    self.playing = False
                    self.running = False
                    self.waiting = False
        elif (self.current_screen == "comic"):
            if (self.current_comic > 16):
                self.waiting = False

    # Draws background and sprites
    def draw(self):
        self.screen.fill(COLOR_SKY)
        self.screen.blit(self.game_background.image, self.game_background.rect.topleft)  # Mountain background
        self.screen.blit(self.img_train_background, self.img_train_background.get_rect())  # Game platform
        self.grp_allSprites.draw(self.screen)

        if (self.pause):
            menu_rect = self.img_pause_menu.get_rect()
            menu_rect.center = (GAME_WIDTH / 2, GAME_HEIGHT / 2)
            self.screen.blit(self.img_pause_menu, menu_rect)
            draw_text(self.screen, "PAUSE", COLOR_WHITE, 50, "center", (GAME_WIDTH / 2, GAME_HEIGHT / 2 - GAME_TILESIZE / 2 - 7))
            for button in self.grp_buttons:
                self.screen.blit(button.image, button.rect)
                draw_text(self.screen, button.name.upper(), COLOR_WHITE, 20, "center", button.rect.center)

        # Shows coin
        img = self.img_player_bullet
        img = pg.transform.scale(img, (int(GAME_TILESIZE * .75), int(GAME_TILESIZE * .75)))
        img.set_colorkey(COLOR_GREEN)
        img_rect = img.get_rect()
        img_rect.topleft = ((GAME_WIDTH / 2) + 15, 10)
        self.screen.blit(img, img_rect)
        draw_text(self.screen, str(self.player.coins), COLOR_BLACK, 20, "topleft", (img_rect.right + 3, img_rect.y + 1))  # 30 in repl, 20 in atom

        # Mob hp
        for sprite in self.grp_mobs:
            if ((sprite.name != "laser") and (sprite.name != "mob boss") and (sprite.name != "rotor")):
                draw_hp(sprite, self.screen, sprite.rect.centerx - (GAME_TILESIZE / 2), sprite.rect.top - 12, GAME_TILESIZE, 8, COLOR_RED)
            elif (sprite.name == "rotor"):
                draw_hp(sprite, self.screen, sprite.extraGraphics.rect.centerx - (GAME_TILESIZE / 2), sprite.extraGraphics.rect.top - 12, GAME_TILESIZE, 8, COLOR_RED)
            elif (sprite.name == "mob boss"):
                draw_hp(sprite, self.screen, 10, (GAME_HEIGHT - (GAME_TILESIZE / 1.5) - 10), (GAME_WIDTH - 20), GAME_TILESIZE / 1.5, COLOR_RED)

        # Player hp
        draw_hp(self.player, self.screen, ((GAME_WIDTH / 2) - (GAME_TILESIZE * 4) - 3), 15, GAME_TILESIZE * 4, 12, COLOR_RED)

        # When level is done
        if ((len(self.grp_mobs) <= 0) and (not self.spawning)):
            draw_text(self.screen, "Press \"O\" to start next wave!", COLOR_BLACK, 30, "center", (GAME_WIDTH / 2, GAME_TILESIZE * 2))

        # When game is won
        if (self.game_won):
            rect = self.img_white_circle.get_rect()
            if (rect.width <= GAME_WIDTH):
                self.img_white_circle = pg.transform.scale(self.img_white_circle, (int(rect.width * 1.2), int(rect.height * 1.2)))
                rect = self.img_white_circle.get_rect()
                rect.center = self.boss.rect.center
                self.screen.blit(self.img_white_circle, rect)
            else:
                self.boss.killSelf()
                self.playing = False
                self.screen.fill(COLOR_WHITE)

        pg.display.flip()

    # Draw screens
    def draw_screens(self):
        now = pg.time.get_ticks()
        #self.screen.fill(COLOR_BLACK)
        if (self.current_screen == "main"):
            self.screen.blit(self.img_main_background, self.img_main_background.get_rect())
        elif (self.current_screen == "htp"):
            self.screen.blit(self.img_htp_background, self.img_htp_background.get_rect())

            menu_rect = self.img_htp_menu.get_rect()
            menu_rect.center = (GAME_WIDTH / 2, GAME_HEIGHT / 2)
            self.screen.blit(self.img_htp_menu, menu_rect)
        elif (self.current_screen == "game_over"):
            self.screen.fill(COLOR_BLACK)
            draw_text(self.screen, "GAME OVER", COLOR_RED, 70, "center", ((GAME_WIDTH / 2), (GAME_HEIGHT / 4) + GAME_TILESIZE))
        elif (self.current_screen == "win"):
            self.screen.fill(COLOR_WHITE)
            if ((now - self.win_text_delay) >= WIN_TEXT_DELAY):
                draw_text(self.screen, "To be", COLOR_BLACK, 85, "center", ((GAME_WIDTH / 2), (GAME_HEIGHT / 4 + (GAME_TILESIZE * 2))))
                draw_text(self.screen, "continued...", COLOR_BLACK, 85, "center", ((GAME_WIDTH / 2), (GAME_HEIGHT * 3 / 4 - (GAME_TILESIZE * 2))))
        elif (self.current_screen == "credits"):
            self.screen.fill(COLOR_WHITE)
            draw_text(self.screen, "Credits", COLOR_BLACK, 55, "topleft", (10, 10))
            draw_text(self.screen, "Made by: j0shWahh", COLOR_BLACK, 40, "topleft", (10, 65))
            draw_text(self.screen, "Font by: Jason Kottke", COLOR_BLACK, 40, "topleft", (10, 95))
            draw_text(self.screen, "Train sound effect:", COLOR_BLACK, 40, "topleft", (10, 130))
            draw_text(self.screen, "    www.get-sounds.com", COLOR_BLACK, 40, "topleft", (10, 155))
            draw_text(self.screen, "Other sound effects:", COLOR_BLACK, 40, "topleft", (10, 190))
            draw_text(self.screen, "    Bxfr", COLOR_BLACK, 40, "topleft", (10, 215))
            draw_text(self.screen, "Repl.it game jam", COLOR_BLACK, 40, "topleft", (10, 377))
            draw_text(self.screen, "April 2019", COLOR_BLACK, 40, "topleft", (10, 407))
        elif (self.current_screen == "comic"):
            if (self.current_comic <= 16):
                img = self.comics[self.current_comic]
                rect = img.get_rect()
                self.screen.blit(img, rect)

        self.grp_allSprites.draw(self.screen)
        for button in self.grp_buttons:
            draw_text(self.screen, button.name.upper(), COLOR_WHITE, 20, "center", button.rect.center)

    # Checks user input in game
    def events(self):
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                self.playing = False
                self.running = False
            if (event.type == pg.KEYDOWN):
                if (event.key == pg.K_ESCAPE):
                    self.playing = False
                    self.current_screen = "main"
                if ((event.key == pg.K_SPACE) or (event.key == pg.K_w) or (event.key == pg.K_UP)):
                    if (not self.pause):
                        self.player.jump()
            if (event.type == pg.KEYUP):
                if ((event.key == pg.K_SPACE) or (event.key == pg.K_w) or (event.key == pg.K_UP)):
                    if (not self.pause):
                        self.player.jump_cut()
                if (event.key == pg.K_o):
                    if ((len(self.grp_mobs) == 0) and (not self.spawning)):
                        self.level += 1
                        self.spawning = True
                if (event.key == pg.K_e):
                    self.spawnNow = True
                    self.spawnNumber += 1
                if (event.key == pg.K_p):
                    #self.pause = not self.pause
                    if (self.pause):
                        Button(self, "pause", (GAME_WIDTH / 2) - GAME_TILESIZE * 3 - GAME_TILESIZE / 4, GAME_HEIGHT / 2 + GAME_TILESIZE / 2, GAME_TILESIZE * 3, GAME_TILESIZE)
                        Button(self, "main menu", (GAME_WIDTH / 2) + GAME_TILESIZE / 4, GAME_HEIGHT / 2 + GAME_TILESIZE / 2, GAME_TILESIZE * 3, GAME_TILESIZE)

                        self.msc_train_tracks.stop()
                    else:
                        self.kill_group(self.grp_buttons)

                        self.msc_train_tracks.play(-1)

        mouse_btn1, mouse_btn2, mouse_btn3 = pg.mouse.get_pressed()
        if (not self.pause):
            if (self.player.current_hp > 0):
                if (mouse_btn1):
                    self.player.shoot()
                if (mouse_btn3):
                    self.mouse_btn3_pressed = True
                else:
                    if (self.mouse_btn3_pressed):
                        self.player.checkShopCollision = True
                        self.mouse_btn3_pressed = False
        else:
            if (mouse_btn1):
                self.mouse_btn1_pressed = True
            else:
                if (self.mouse_btn1_pressed):
                    self.mouse_btn1_pressed = False
                    for button in self.grp_buttons:
                        button.checkClick()

                    if (not self.pause):
                        self.msc_train_tracks.play(-1)

    # Check user input in screen
    def events_screens(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        mouse_btn1, mouse_btn2, mouse_btn3 = pg.mouse.get_pressed()
        if (mouse_btn1):
            self.mouse_btn1_pressed = True
        else:
            if (self.mouse_btn1_pressed):
                self.mouse_btn1_pressed = False
                if (self.current_screen == "comic"):
                    self.current_comic += 1
                elif (self.current_screen != "main"):
                    for button in self.grp_buttons:
                        button.checkClick()
                else:
                    if (len(self.grp_playerBullets) <= 0):
                        angle = get_angle(self.player, mouse_x, mouse_y)
                        Bullet(self.player, self, angle, 23, 175)

        for event in pg.event.get():
            if (event.type == pg.QUIT):
                self.running = False
                self.waiting = False
            if (event.type == pg.KEYDOWN):
                if (self.current_screen != "comic"):
                    if (event.key == pg.K_ESCAPE):
                        if (self.current_screen == "main"):
                            self.running = False
                            self.waiting = False
                        else:
                            if (self.current_screen != "win"):
                                self.playing = False
                                self.waiting = False
                                self.current_screen = "main"
                            else:
                                self.playing = False
                                self.waiting = False
                                self.current_screen = "credits"
                else:
                    if (event.key == pg.K_ESCAPE):
                        self.playing = False
                        self.waiting = False
                        self.playing = False
                        self.current_screen = "main"
                    else:
                        self.current_comic += 1

    # Checks user input in menu
    def wait_for_key(self):
        self.mouse_btn1_pressed = False
        self.waiting = True
        while (self.waiting):
            self.dt = self.clock.tick(GAME_FPS) / 1000
            # Menu user input checking
            self.events_screens()

            # Menu draw background and sprites
            self.draw_screens()

            # Update
            self.update_screens()

            pg.display.flip()

        if (self.current_screen != "comic"):
            self.kill_group(self.grp_allSprites)

            if (self.playing):
                self.run()

    # Shows screens (main menu, game over, win...)
    def show_screens(self):
        if (self.current_screen == "main"):
            self.player = ExtraGraphics(None, self, "menu gun", "center", 0, 0)
        elif (self.current_screen == "game_over"):
            # x = desiredPosition - width/2       y = desirePosition - height/2
            Button(self, "play again", int((GAME_WIDTH / 4) - GAME_TILESIZE * 6 / 2), int((GAME_HEIGHT * 3 / 4) - GAME_TILESIZE) - GAME_TILESIZE, GAME_TILESIZE * 6, GAME_TILESIZE * 2)
            Button(self, "main menu", int((GAME_WIDTH * 3/ 4) - GAME_TILESIZE * 6 / 2), int((GAME_HEIGHT * 3 / 4) - GAME_TILESIZE) - GAME_TILESIZE, GAME_TILESIZE * 6, GAME_TILESIZE * 2)

        self.wait_for_key()


g = Game()

while g.running:
    g.screen_name = "main"
    g.show_screens()
