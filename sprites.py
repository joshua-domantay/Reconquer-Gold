import pygame as pg
import math
import random
from settings import *

vec = pg.math.Vector2

def spawnMob(game, mob_name, direction):
    if (mob_name == "head"):
        if (direction == "left"):
            Mob(game, "head", MOB_HEAD_STARTX, (GAME_TILESIZE * random.randrange(4, 9)))
        else:
            Mob(game, "head", (GAME_WIDTH - MOB_HEAD_STARTX), (GAME_TILESIZE * random.randrange(4, 9)))
    elif (mob_name == "guard"):
        if (direction == "left"):
            Mob(game, "guard", MOB_GUARD_STARTX, MOB_GUARD_STARTY)
        else:
            Mob(game, "guard", (GAME_WIDTH - MOB_GUARD_STARTX), MOB_GUARD_STARTY)
    elif (mob_name == "rotor"):
        if (direction == "left"):
            Mob(game, "rotor", MOB_ROTOR_STARTX, MOB_ROTOR_STARTY)
        else:
            Mob(game, "rotor", GAME_WIDTH - MOB_ROTOR_STARTX, MOB_ROTOR_STARTY)
    elif (mob_name == "laser"):
        if (direction == "left"):
            Mob(game, "laser", MOB_LASER_LEFT, MOB_LASER_STARTY)
        else:
            Mob(game, "laser", MOB_LASER_RIGHT, MOB_LASER_STARTY)

# degree or angle of mouse
def get_angle(sprite, target_x, target_y):
    if (target_y > sprite.rect.centery):
        y_distance = -sprite.rect.centery + target_y
    else:
        y_distance = sprite.rect.centery - target_y
    if (target_x > sprite.rect.centerx):
        x_distance = -sprite.rect.centerx + target_x
    else:
        x_distance = sprite.rect.centerx - target_x

    if (x_distance == 0):
        if (target_y > sprite.rect.centery):
            angle = 270
        if (target_y < sprite.rect.centery):
            angle = 90
    else:
        angle = math.degrees(math.atan(y_distance / x_distance))
        if ((target_x < sprite.rect.centerx) and (target_y > sprite.rect.centery)):
            angle = 180 + angle
        elif ((target_x > sprite.rect.centerx) and (target_y > sprite.rect.centery)):
            angle = 360 - angle
        elif (target_x < sprite.rect.centerx):
            angle = 180 - angle

    return angle

def collide_group(sprite, group):
    hits = pg.sprite.spritecollide(sprite, group, False)
    if (hits):
        if (sprite.name == "player"):
            if (group == sprite.game.grp_walls):
                if (sprite.vel.y >= 0):
                    if (sprite.rect.bottom >= sprite.last_platform.rect.y):
                        if (sprite.last_platform.name == "game_ground"):
                            sprite.acc.y = 0
                            sprite.vel.y = 0
                            sprite.pos.y = hits[0].rect.top
                            sprite.jumping = False
                            sprite.collided = True
                        # So player will not glitch when jumping on floating platforms
                        elif (sprite.rect.bottom - 10 <= sprite.last_platform.rect.y):
                            sprite.acc.y = 0
                            sprite.vel.y = 0
                            sprite.pos.y = hits[0].rect.top
                            sprite.jumping = False
                            sprite.collided = True
                sprite.last_platform = hits[0]
            elif (group == sprite.game.grp_mobLasers):
                sprite.current_hp -= DAMAGE_LASER
            else:
                sprite.current_hp -= DAMAGE_BULLET_PLAYER
                sprite.game.snd_player_hit.stop()
                sprite.game.snd_player_hit.play()
                hits[0].killSelf()
        else:
            sprite.current_hp -= DAMAGE_BULLET_MOB
            hits[0].killSelf()

def collide_rect(sprite, otherSprite):
    hits = pg.sprite.collide_rect(sprite, otherSprite)
    if (hits):
        if (sprite.name == "player"):
            if (sprite.coins >= 100):
                sprite.coins -= 100
                sprite.current_hp = PLAYER_MAX_HP
                sprite.game.snd_hp.stop()
                sprite.game.snd_hp.play()
            sprite.checkShopCollision = False
        elif (sprite.name == "laser"):
            sprite.killSelf()
    else:
        if (sprite.name == "player"):
            sprite.checkShopCollision = False


# To get images from spritesheet
class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.set_colorkey(COLOR_GREEN)
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return image


# To show imgs like player gun, "rotor" mob rotating body, etc...
class ExtraGraphics(pg.sprite.Sprite):
    def __init__(self, sprite, game, name, position, x, y):
        self.sprite = sprite
        self.game = game
        self.name = name
        self.position = position
        if (self.name != "game_background"):
            self.groups = self.game.grp_allSprites
            pg.sprite.Sprite.__init__(self, self.groups)
        else:
            pg.sprite.Sprite.__init__(self)
        self.load_data(x, y)

    def load_data(self, x, y):
        self.current_frame = 0
        self.last_frame = 0

        if (self.name == "player_body"):
            self.offset = vec(-PLAYER_BODY_OFFSET_X, 0)
            self.image_list = [self.game.spritesheet.get_image((34 * 0), 0, 34, 78),
                               self.game.spritesheet.get_image((34 * 1), 0, 34, 78),
                               self.game.spritesheet.get_image((34 * 2), 0, 34, 78),
                               self.game.spritesheet.get_image((34 * 3), 0, 34, 78),
                               self.game.spritesheet.get_image((34 * 4), 0, 34, 78),
                               self.game.spritesheet.get_image((34 * 5), 0, 34, 78),
                               self.game.spritesheet.get_image((34 * 6), 0, 34, 78),
                               self.game.spritesheet.get_image((34 * 7), 0, 34, 78)]
            self.image_jump = self.game.spritesheet.get_image(0, 335, 34, 78)
            self.image = self.image_list[0]
        elif (self.name == "player_gun"):
            self.offset = vec(2, 18)
            self.image = self.game.img_player_gun
        elif (self.name == "menu gun"):
            self.offset = vec(25, 168)
            self.image = self.game.img_player_gun
            self.image = pg.transform.scale(self.image, (336, 336))
        elif (self.name == "mob boss gun"):
            self.offset = vec(0, 7)
            self.image = self.game.img_mob_boss_gun
        elif (self.name == "laser"):
            self.offset = vec(0, 0)
            self.image_list = [self.game.spritesheet.get_image((12 * 0), 112, 12, 32),
                               self.game.spritesheet.get_image((12 * 1), 112, 12, 32),
                               self.game.spritesheet.get_image((12 * 2), 112, 12, 32),
                               self.game.spritesheet.get_image((12 * 3), 112, 12, 32)]
            self.image = self.image_list[0]
        elif (self.name == "guard_gun"):
            self.offset = vec(2, 20)
            self.image = self.game.img_guard_gun
        elif (self.name == "rotor_bullet"):
            self.rotation = random.randrange(0, 360)
            self.image = self.game.img_rotor_bullet
        elif (self.name == "guard_board"):
            self.image = self.game.img_guard_board
        elif (self.name == "rotor_main"):
            self.image = self.game.img_rotor_main
        elif (self.name == "game_ground"):
            self.image = self.game.img_ground
            self.vel = vec(-GROUND_SPEED, 0)
            self.pos = (x, y)
        elif (self.name == "game_background"):
            self.image = self.game.img_game_background
            self.vel = vec(-GAME_BACKGROUND_SPEED, 0)
            self.pos = (x, y)

        self.image.set_colorkey(COLOR_GREEN)
        self.rect = self.image.get_rect()

        if (self.position == "center"):
            self.rect.center = (x, y)
        elif (self.position == "midbottom"):
            self.rect.midbottom = (x, y)
        elif (self.position == "bottomleft"):
            self.rect.bottomleft = (x, y)

        if (self.name == "guard_board"):
            self.rect.x += GAME_WIDTH * 2
        elif (self.name == "menu gun"):
            self.rect.x += self.offset.x
            self.rect.y += self.offset.y

    def animate(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        now = pg.time.get_ticks()
        if (self.position == "center"):
            center = self.rect.center
        elif (self.position == "midbottom"):
            midbottom = self.rect.midbottom

        if (now - self.last_frame >= 70):
            if (self.name == "player_body"):
                if (self.sprite.moving):
                    if (not self.sprite.jumping):
                        self.last_frame = now
                        self.current_frame += 1

                        if (self.sprite.facing_left):
                            self.image = pg.transform.flip(self.image_list[self.current_frame % len(self.image_list)], True, False)
                            self.offset = vec(PLAYER_BODY_OFFSET_X, 0)
                        else:
                            self.image = self.image_list[self.current_frame % len(self.image_list)]
                            self.offset = vec(-PLAYER_BODY_OFFSET_X, 0)
                    else:
                        if (self.sprite.facing_left):
                            self.image = pg.transform.flip(self.image_jump, True, False)
                            self.offset = vec(PLAYER_BODY_OFFSET_X, 0)
                        else:
                            self.image = self.image_jump
                            self.offset = vec(-PLAYER_BODY_OFFSET_X, 0)
                else:
                    if (self.sprite.facing_left):
                        self.image = pg.transform.flip(self.image_list[0], True, False)
                        self.offset = vec(PLAYER_BODY_OFFSET_X, 0)
                    else:
                        self.image = self.image_list[0]
                        self.offset = vec(-PLAYER_BODY_OFFSET_X, 0)
            elif (self.name == "player_gun"):
                if (self.sprite.facing_left):
                    self.image = pg.transform.flip(self.game.img_player_gun, False, True)
                    self.offset = vec(14, 18)
                else:
                    self.image = self.game.img_player_gun
                    self.offset = vec(2, 18)

                angle = get_angle(self, mouse_x, mouse_y)
                self.image = pg.transform.rotate(self.image, angle)
            elif (self.name == "menu gun"):
                self.image = self.game.img_player_gun
                self.image = pg.transform.scale(self.image, (336, 336))

                angle = get_angle(self, mouse_x, mouse_y)
                self.image = pg.transform.rotate(self.image, angle)
            elif (self.name == "mob boss gun"):
                if (self.sprite.current_hp > 0):
                    self.image = self.game.img_mob_boss_gun

                    angle = get_angle(self, self.game.player.rect.centerx, self.game.player.rect.centery)
                    self.image = pg.transform.rotate(self.image, angle)
            elif (self.name == "guard_gun"):
                if (self.sprite.facing_left):
                    self.image = pg.transform.flip(self.game.img_guard_gun, False, True)
                    self.offset = vec(14, 20)
                else:
                    self.image = self.game.img_guard_gun
                    self.offset = vec(2, 20)

                angle = get_angle(self.sprite, self.game.player.rect.centerx, self.game.player.rect.centery)
                self.image = pg.transform.rotate(self.image, angle)
            elif (self.name == "rotor_bullet"):
                self.rotation += ROTOR_BULLET_ROTATION
                self.rotation %= 360
                self.image = pg.transform.rotate(self.game.img_rotor_bullet, self.rotation)
            elif (self.name == "laser"):
                self.last_frame = now
                self.current_frame += 1
                self.image = self.image_list[self.current_frame % len(self.image_list)]

            self.rect = self.image.get_rect()

            if (self.position == "center"):
                self.rect.center = center
            elif (self.position == "midbottom"):
                self.rect.midbottom = midbottom

        self.image.set_colorkey(COLOR_GREEN)

    def killSelf(self):
        self.kill()

    def update(self):
        self.animate()

        if (self.name == "player_body"):
            self.rect.centerx = self.sprite.rect.centerx + self.offset.x
            self.rect.centery = self.sprite.rect.centery + self.offset.y
        elif ((self.name == "player_gun") or (self.name == "guard_gun")):
            self.rect.centerx = self.sprite.rect.x + self.offset.x
            self.rect.centery = self.sprite.rect.y + self.offset.y
        elif (self.name == "mob boss gun"):
            self.rect.center = self.sprite.rect.center + self.offset
        elif (self.name == "guard_board"):
            self.rect.midtop = self.sprite.rect.midbottom
        elif (self.name == "laser"):
            self.rect.midbottom = self.sprite.rect.midbottom
        elif (self.name == "rotor_main"):
            self.rect.center = self.sprite.rect.center
        elif (self.name == "rotor_bullet"):
            self.rect.center = self.sprite.rect.center
        elif ((self.name == "game_ground") or (self.name == "game_background")):
            self.pos += self.vel * self.game.dt
            self.rect.x = self.pos.x
            self.rect.y = self.pos.y - self.rect.height
            if (self.rect.right <= GAME_WIDTH):
                self.rect.left = 0
                self.pos.x = 0


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.name = "player"
        self.groups = self.game.grp_allSprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_data(x, y)

    def load_data(self, x, y):
        self.moving = True
        self.jumping = True
        self.jumpDown = False
        self.collided = False
        self.checkShopCollision = False
        self.boughtHp = False
        self.facing_left = False
        self.last_shot = 0
        self.coins = PLAYER_STARTING_COINS
        self.current_hp = PLAYER_MAX_HP
        self.original_hp = PLAYER_MAX_HP
        self.last_platform = self.game.ground

        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.image = self.game.img_player
        self.image.set_colorkey(COLOR_GREEN)
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.pos

        # ExtraGraphics needed for player
        self.body = ExtraGraphics(self, self.game, "player_body", "center", self.rect.centerx, self.rect.centery)
        self.gun = ExtraGraphics(self, self.game, "player_gun", "center", self.rect.x, self.rect.y)

    def get_keys(self):
        keys = pg.key.get_pressed()

        if (keys[pg.K_a] or keys[pg.K_LEFT]):
            self.acc.x = -PLAYER_ACCELERATION
        if (keys[pg.K_d] or keys[pg.K_RIGHT]):
            self.acc.x = PLAYER_ACCELERATION
        if ((self.collided) and (self.vel.y == 0)):
            if ((keys[pg.K_s] or keys[pg.K_DOWN]) and (self.last_platform.name != "ground")):
                self.jumpDown = True
                self.collided = False

    def jump(self):
        if (not self.jumping):
            self.vel.y = -PLAYER_JUMP
            self.jumping = True

    def jump_cut(self):
        if ((self.jumping) and (self.vel.y < -PLAYER_JUMP_CUT)):
            self.vel.y = -PLAYER_JUMP_CUT

    def shoot(self):
        now = pg.time.get_ticks()
        mouse_x, mouse_y = pg.mouse.get_pos()

        if (self.coins > 0):
            if (now - self.last_shot >= PLAYER_SHOOT_DELAY):
                self.last_shot = now
                self.coins -= 1
                angle = get_angle(self.gun, mouse_x, mouse_y)
                Bullet(self, self.game, angle, 0, 0)

    def checkCollision(self):
        collide_group(self, self.game.grp_mobBullets)
        collide_group(self, self.game.grp_mobLasers)

        if (not self.jumpDown):
            collide_group(self, self.game.grp_walls)
        else:
            self.jumping = True
            if (self.rect.top >= self.last_platform.rect.bottom):
                self.jumpDown = False

        if (self.checkShopCollision):
            collide_rect(self, self.game.shop)

    def animate(self):
        center = self.rect.center

        if (self.facing_left):
            self.image = pg.transform.flip(self.game.img_player, True, False)
        else:
            self.image = self.game.img_player

        self.image.set_colorkey(COLOR_GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def killSelf(self):
        self.body.killSelf()
        self.gun.killSelf()
        self.kill()

    def update(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        self.animate()

        if (self.game.level == 10):
            if (not (self.game.boss.current_hp <= 0)):
                self.checkCollision()
        else:
            self.checkCollision()

        if self.jumping:
            self.acc = vec(0, GRAVITY)
        else:
            self.acc = vec(0, 0)
            if ((self.rect.x >= (self.last_platform.rect.x + self.last_platform.rect.width)) or ((self.rect.x + self.rect.width) <= self.last_platform.rect.x)):
                self.jumping = True
                self.jumpDown = True

        self.get_keys()

        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        if (abs(self.vel.x) < 0.1):
            self.vel.x = 0
        self.pos += self.vel

        self.rect.midbottom = self.pos
        if (self.rect.left <= 0):
            self.rect.left = 0
            self.pos.x = self.rect.width / 2
        if (self.rect.right >= GAME_WIDTH):
            self.rect.right = GAME_WIDTH
            self.pos.x = GAME_WIDTH - (self.rect.width / 2)
        if (self.rect.bottom >= self.game.ground.rect.top):
            self.acc.y = 0
            self.vel.y = 0
            self.pos.y = self.game.ground.rect.top
            self.jumping = False
            self.collided = True
            self.last_platform = self.game.ground

        if (self.current_hp <= 0):
            self.killSelf()

        if ((self.vel.x == 0) and (self.vel.y == 0)):
            self.moving = False
        else:
            self.moving = True

        if (mouse_x <= self.rect.centerx):
            self.facing_left = True
        else:
            self.facing_left = False


class MobBoss(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.name = "mob boss"
        self.groups = self.game.grp_allSprites, self.game.grp_mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_data(x, y)

    def load_data(self, x, y):
        self.shooting_lasers = False
        self.move_now = True
        self.last_shot_lasers = 0
        self.last_shot_rotor = 0
        self.last_shot_gun = 0
        self.last_mob_spawn = 0
        self.last_frame = 0
        self.current_frame = 0
        self.pos = vec(x, y)
        self.vel = vec(0, 0)  # Left or right random
        self.current_hp = BOSS_MAX_HP
        self.original_hp = BOSS_MAX_HP
        self.bullet_name = "none"

        self.image_list = [self.game.spritesheet.get_image((324 + 154 * 0), 0, 154, 68),
                           self.game.spritesheet.get_image((324 + 154 * 1), 0, 154, 68),
                           self.game.spritesheet.get_image((324 + 154 * 2), 0, 154, 68),
                           self.game.spritesheet.get_image((324 + 154 * 0), 68, 154, 68),
                           self.game.spritesheet.get_image((324 + 154 * 1), 68, 154, 68),
                           self.game.spritesheet.get_image((324 + 154 * 2), 68, 154, 68),
                           self.game.spritesheet.get_image((324 + 154 * 3), 68, 154, 68)]
        self.image = self.image_list[0]
        self.image.set_colorkey(COLOR_GREEN)
        self.rect = self.image.get_rect()
        self.rect.midtop = self.pos

        self.gun = ExtraGraphics(self, self.game, "mob boss gun", "center", self.rect.centerx, self.rect.centery)

    def move(self):
        if (self.pos.y < GAME_TILESIZE):
            self.vel.y = BOSS_SPEED
        else:
            if (self.move_now):
                self.vel.x = BOSS_SPEED * random.randrange(-1, 2, 2)
                self.move_now = False
            if (self.current_hp > 0):
                self.vel.y = 0
                if (self.rect.left <= (GAME_TILESIZE / 2)):
                    self.vel.x = BOSS_SPEED
                elif (self.rect.right >= (GAME_WIDTH - (GAME_TILESIZE / 2))):
                    self.vel.x = -BOSS_SPEED
            else:
                if (self.rect.bottom < GAME_HEIGHT - (GAME_TILESIZE * 2.5)):
                    self.acc = vec(0, BOSS_CRASH_ACC)
                else:
                    self.acc = vec(0, 0)
                    self.pos.y = GAME_HEIGHT - (GAME_TILESIZE * 2.5) - self.rect.height
                    self.game.game_won = True
                self.vel.x = 0
                self.vel += self.acc

        self.pos += self.vel * self.game.dt
        self.rect.midtop = self.pos

    def shoot(self):
        now = pg.time.get_ticks()

        if ((now - self.last_shot_lasers) >= BOSS_SHOOT_LASER_DELAY):
            if (not self.shooting_lasers):
                Laser(self, self.game, 13, self.rect.bottom)
                Laser(self, self.game, 137, self.rect.bottom)
                self.shooting_lasers = True
            if ((now - self.last_shot_lasers) >= BOSS_SHOOT_LASER_DURATION):
                self.last_shot_lasers = now + random.randrange(-100, 550, 50)
                self.shooting_lasers = False
        if ((now - self.last_shot_rotor) >= BOSS_SHOOT_ROTOR_DELAY):
            self.bullet_name = "rotor"
            self.last_shot_rotor = now + random.randrange(-100, 550, 50)
            for angle in range(225, 316, 45):
                Bullet(self, self.game, angle, self.rect.centerx, self.rect.bottom)
        if ((now - self.last_shot_gun) >= BOSS_SHOOT_GUN_DELAY):
            self.bullet_name = "gun"
            self.last_shot_gun = now + random.randrange(-100, 550, 50)
            angle = get_angle(self, self.game.player.rect.centerx, self.game.player.rect.centery)
            Bullet(self, self.game, angle, self.rect.centerx, self.rect.bottom)

    def animate(self):
        now = pg.time.get_ticks()

        if ((now - self.last_frame) >= 25):
            self.last_frame = now
            self.current_frame += 1
            self.image = self.image_list[self.current_frame % len(self.image_list)]
            self.image.set_colorkey(COLOR_GREEN)
            self.rect = self.image.get_rect()
            self.rect.midtop = self.pos

    def checkCollision(self):
        if (self.current_hp > 0):
            collide_group(self, self.game.grp_playerBullets)
        else:
            self.current_hp = 0
            self.shooting_lasers = False

    def spawnMob(self):
        now = pg.time.get_ticks()

        if ((now - self.last_mob_spawn) >= BOSS_SPAWN_DELAY):
            self.last_mob_spawn = now + random.randrange(0, 4500, 500)

            if (len(self.game.grp_mobs) == 1):
                randInt = random.randrange(4)
                if (randInt == 3):
                    randInt = random.randrange(7)
                    if (randInt == 0):
                        randInt = random.randrange(2)
                        if (randInt == 0):
                            spawnMob(self.game, "guard", "left")
                        else:
                            spawnMob(self.game, "guard", "right")
                    elif (randInt == 1):
                        spawnMob(self.game, "guard", "left")
                        spawnMob(self.game, "guard", "right")
                    elif (randInt == 2):
                        spawnMob(self.game, "head", "left")
                    elif (randInt == 3):
                        spawnMob(self.game, "head", "right")
                    elif (randInt == 4):
                        spawnMob(self.game, "head", "left")
                        spawnMob(self.game, "head", "right")
                    elif (randInt == 5):
                        spawnMob(self.game, "head", "left")
                        spawnMob(self.game, "guard", "right")
                    elif(randInt == 6):
                        spawnMob(self.game, "guard", "left")
                        spawnMob(self.game, "head", "right")

    def killSelf(self):
        self.gun.killSelf()
        self.kill()


    def update(self):
        self.animate()
        self.move()

        if ((self.current_hp > 0) and (not self.move_now)):
            self.shoot()

        self.spawnMob()
        self.checkCollision()


class Mob(pg.sprite.Sprite):
    def __init__(self, game, name, x, y):
        self.game = game
        self.name = name
        self.groups = self.game.grp_allSprites, self.game.grp_mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_data(x, y)

    def load_data(self, x, y):
        self.shooting = False
        self.last_shot = 0
        self.last_frame = 0
        self.current_frame = 0

        # Specifically only for "guard" mob
        if (x < (GAME_WIDTH / 2)):
            self.facing_left = True
        else:
            self.facing_left = False
        self.shoot_once = True  # Specifically only for "laser" mob
        self.extraGraphics = 0  # Specifically only for "laser" mob
        self.initiated = True  # Specifically only for "laser" and "rotor" mob
        self.rotation = 0  # Specifically only for "rotor" mob

        self.vel = vec(0, 0)
        self.pos = vec(x, y)

        if (self.name == "head"):
            if (self.pos.x > (GAME_WIDTH / 2)):
                self.image = self.game.img_head
            else:
                self.image = pg.transform.flip(self.game.img_head, True, False)
            self.rect = self.image.get_rect()
            self.current_hp = MOB_HEAD_MAX_HP
            self.original_hp = MOB_HEAD_MAX_HP
            if (x > 0):  # If mob is at the right
                self.pos.x -= self.rect.width

        if (self.name == "guard"):
            self.image_list = [self.game.spritesheet.get_image((18 * 0), 144, 18, 80),
                               self.game.spritesheet.get_image((18 * 1), 144, 18, 80),
                               self.game.spritesheet.get_image((18 * 2), 144, 18, 80),
                               self.game.spritesheet.get_image((18 * 3), 144, 18, 80)]
            # Used for when facing opposite direction instead of animating
            self.current_frame = random.randrange(len(self.image_list))
            self.image = self.image_list[self.current_frame]
            self.rect = self.image.get_rect()
            self.extraGraphics = ExtraGraphics(self, self.game, "guard_gun", "center", self.pos.x, self.pos.y)
            self.board = ExtraGraphics(self, self.game, "guard_board", "midbottom", self.rect.centerx, self.rect.bottom)
            self.current_hp = MOB_GUARD_MAX_HP
            self.original_hp = MOB_GUARD_MAX_HP
            if (x > 0):  # If mob is at the right
                self.pos.x -= self.rect.width
            self.pos.y -= self.rect.height

        if (self.name == "rotor"):
            self.image = self.game.img_rotor_body
            self.rect = self.image.get_rect()
            self.extraGraphics = ExtraGraphics(self, self.game, "rotor_main", "center", self.pos.x, self.pos.y)
            self.current_hp = MOB_ROTOR_MAX_HP
            self.original_hp = MOB_ROTOR_MAX_HP
            if (x > 0):  # If mob is at the right
                self.pos.x -= self.rect.width

        if (self.name == "laser"):
            self.image_list = [self.game.spritesheet.get_image((62 * 0), 78, 62, 34),
                               self.game.spritesheet.get_image((62 * 1), 78, 62, 34),
                               self.game.spritesheet.get_image((62 * 2), 78, 62, 34),
                               self.game.spritesheet.get_image((62 * 3), 78, 62, 34),
                               self.game.spritesheet.get_image((62 * 4), 78, 62, 34)]
            self.image = self.image_list[0]
            self.rect = self.image.get_rect()
            self.current_hp = 1
            if (x > (GAME_WIDTH / 2)):  # If mob is at the right
                self.pos.x -= self.rect.width

        self.image.set_colorkey(COLOR_GREEN)
        self.rect.topleft = self.pos

    def move(self):
        now = pg.time.get_ticks()

        if (self.name == "head"):
            if (self.rect.right <= (GAME_TILESIZE + (GAME_TILESIZE / 3))):
                self.vel.x = MOB_HEAD_SPEEDX
            elif (self.rect.x >= (GAME_WIDTH - self.rect.width - (GAME_TILESIZE / 3))):
                self.vel.x = -MOB_HEAD_SPEEDX
            else:
                self.shooting = True
                self.vel.x = 0
                if (self.vel.y == 0):
                    self.vel.y = MOB_HEAD_SPEEDY * random.randrange(-1, 2, 2)

                if (self.pos.y <= (GAME_TILESIZE * 4)):
                    self.vel.y = MOB_HEAD_SPEEDY
                elif (self.rect.bottom >= (GAME_HEIGHT - (GAME_TILESIZE * 3))):
                    self.vel.y = -MOB_HEAD_SPEEDY

        if (self.name == "guard"):
            if (self.rect.right <= (GAME_TILESIZE + (GAME_TILESIZE * 2.5))):
                self.vel.x = MOB_GUARD_SPEED
            elif (self.rect.x >= (GAME_WIDTH - self.rect.width - (GAME_TILESIZE * 2.5))):
                self.vel.x = -MOB_GUARD_SPEED
            else:
                self.shooting = True
                self.vel.x = 0

        if (self.name == "rotor"):
            if ((self.rect.x <= (GAME_TILESIZE * 3 /4)) and (self.initiated)):
                self.vel = vec(MOB_ROTOR_SPEED, MOB_ROTOR_SPEED)
            elif ((self.rect.right >= (GAME_WIDTH - (GAME_TILESIZE * 3 / 4))) and (self.initiated)):
                self.vel = vec(-MOB_ROTOR_SPEED, MOB_ROTOR_SPEED)
            else:
                self.initiated = False
                self.shooting = True
                self.vel = vec(0, 0)

                # Rotates "rotor" mob
                self.rotation += MOB_ROTOR_SPEEDR * self.game.dt

        if (self.name == "laser"):
            if ((self.rect.y <= (GAME_TILESIZE / 2)) and self.initiated):
                self.vel.y = MOB_LASER_SPEEDY
                self.last_shot = now
            else:
                self.initiated = False
                self.vel.y = 0

                if (now - self.last_shot >= 5000):
                    # Shooting
                    self.shooting = True
                    if (self.pos.x == ((GAME_WIDTH * 3 / 4) - self.rect.width)):
                        self.vel.x = -MOB_LASER_SPEEDX
                    elif (self.pos.x == (GAME_WIDTH / 4)):
                        self.vel.x = MOB_LASER_SPEEDX

                    # Stop shooting
                    if ((self.vel.x <= 0) and (self.pos.x <= (GAME_WIDTH / 4))):
                        self.vel.x = 0
                        self.vel.y = -MOB_LASER_SPEEDY
                        self.shooting = False
                        # Die... or self.load_data() again? Keep original (x, y) for laser?
                    elif ((self.vel.x >= 0) and ((self.pos.x + self.rect.width) >= (GAME_WIDTH * 3 / 4))):
                        self.vel.x = 0
                        self.vel.y = -MOB_LASER_SPEEDY
                        self.shooting = False

        if (self.shooting):
            self.shoot()

        # Movement speed
        if (self.name == "rotor"):  # Takes care of "rotor" mob rotation
            if (self.initiated):
                self.pos += self.vel * self.game.dt
                self.rect.topleft = self.pos
        else:
            self.pos += self.vel * self.game.dt
            self.rect.topleft = self.pos

    def shoot(self):
        now = pg.time.get_ticks()

        # Randomize shooting = Not constant
        if (self.name == "head"):
            if (now - self.last_shot >= HEAD_SHOOT_DELAY):
                self.last_shot = now
                self.last_shot += random.randrange(-150, 300, 25)  # So shooting is not constant
                if (self.rect.x > (GAME_WIDTH / 2)):
                    Bullet(self, self.game, 0, self.rect.x, self.rect.centery)
                else:
                    Bullet(self, self.game, 0, self.rect.right, self.rect.centery)
        if (self.name == "guard"):
            if (now - self.last_shot >= GUARD_SHOOT_DELAY):
                self.last_shot = now
                self.last_shot += random.randrange(-150, 300, 25)  # So shooting is not constant
                angle = get_angle(self, self.game.player.rect.centerx, self.game.player.rect.centery)
                Bullet(self, self.game, angle, 0, 0)
        if (self.name == "rotor"):
            if (now - self.last_shot >= ROTOR_SHOOT_DELAY):
                self.last_shot = now
                for i in range(0, 360, 45):
                    angle = (self.rotation + i) % 360
                    Bullet(self, self.game, angle, 0, 0)
        if (self.name == "laser"):
            if (self.shoot_once):
                self.shoot_once = False
                self.extraGraphics = Laser(self, self.game, self.rect.centerx, self.rect.bottom)

    def animate(self):
        now = pg.time.get_ticks()
        center = self.rect.center
        pos = self.pos

        if (self.name == "laser"):
            if (now - self.last_frame >= 50):
                self.last_frame = now
                self.current_frame += 1
                self.image = self.image_list[self.current_frame % len(self.image_list)]
        elif (self.name == "rotor"):
            self.image = pg.transform.rotate(self.game.img_rotor_body, self.rotation)
        elif (self.name == "guard"):
            if (self.facing_left):
                self.image = pg.transform.flip(self.image_list[self.current_frame], True, False)
            else:
                self.image = self.image_list[self.current_frame]

        self.image.set_colorkey(COLOR_GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.pos = pos

    def checkCollision(self):
        if (self.name == "laser"):
            collide_rect(self, self.game.player)
        else:
            collide_group(self, self.game.grp_playerBullets)

    def killSelf(self):
        if ((self.name == "laser") or (self.name == "rotor") or (self.name == "guard")):
            if (self.extraGraphics != 0):
                self.extraGraphics.killSelf()
            if (self.name == "guard"):
                self.board.killSelf()

        # Add coins to player
        if (self.name == "head"):
            self.game.player.coins += 15
        elif (self.name == "guard"):
            self.game.player.coins += 25
        elif (self.name == "rotor"):
            self.game.player.coins += 25
        elif (self.name == "laser"):
            self.game.player.coins += 5

        # Sound
        self.game.snd_mob_dead.stop()
        self.game.snd_mob_dead.play()

        self.kill()

    def update(self):
        self.move()

        self.checkCollision()

        if (self.name == "laser"):
            if ((self.rect.bottom <= 0) and (not self.initiated)):
                self.killSelf()

        if (self.current_hp <= 0):
            self.killSelf()

        if (self.name == "guard"):
            if (self.game.player.rect.centerx <= self.rect.centerx):
                self.facing_left = True
            else:
                self.facing_left = False

        self.animate()


class Bullet(pg.sprite.Sprite):
    def __init__(self, sprite, game, angle, x, y):
        self.game = game
        self.sprite = sprite
        self.angle = angle
        self.name = "bullet"
        if ((self.sprite.name == "player") or (self.sprite.name == "menu gun")):
            self.groups = self.game.grp_allSprites, self.game.grp_playerBullets
        else:
            self.groups = self.game.grp_allSprites, self.game.grp_mobBullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_data(x, y)

    def load_data(self, x, y):
        if (self.sprite.name == "player"):
            self.pos = vec(self.sprite.gun.rect.centerx, self.sprite.gun.rect.centery)
            offset = vec((self.sprite.gun.rect.width / 2) - 20, 0)
            self.pos += offset.rotate(-self.angle)

            self.image = self.game.img_player_bullet
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.vel = vec(BULLET_PLAYER_SPEED, 0)

            self.vel = self.vel.rotate(-self.angle)

            # Sound
            self.game.snd_bullet_coin.stop()
            self.game.snd_bullet_coin.play()

        elif (self.sprite.name == "menu gun"):
            self.pos = vec(self.sprite.rect.centerx, self.sprite.rect.centery)
            offset = vec((self.sprite.rect.width / 2) - 20, 0)
            self.pos += offset.rotate(-self.angle)

            self.image = self.game.img_player_bullet
            self.image = pg.transform.scale(self.image, (self.image.get_rect().width * 4, self.image.get_rect().height * 4))
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.vel = vec(BULLET_PLAYER_SPEED * 1.5, 0)

            self.vel = self.vel.rotate(-self.angle)

            # Sound
            self.game.snd_bullet_coin.stop()
            self.game.snd_bullet_coin.play()

        elif ((self.sprite.name == "guard") or (self.sprite.name == "rotor")):
            if (self.sprite.name == "guard"):
                self.pos = vec(self.sprite.extraGraphics.rect.centerx, self.sprite.extraGraphics.rect.centery)
                offset = vec((self.sprite.extraGraphics.rect.width / 2), 0)
            else:
                self.pos = vec(self.sprite.rect.centerx, self.sprite.rect.centery)
                offset = vec(self.sprite.rect.width / 2, 0)
            self.pos += offset.rotate(-self.angle)

            if (self.sprite.name == "guard"):
                self.image = self.game.img_player_bullet
                self.vel = vec(BULLET_GUARD_SPEED, 0)

                # Sound
                self.game.snd_bullet_coin.stop()
                self.game.snd_bullet_coin.play()
            else:
                self.image = pg.Surface((GAME_TILESIZE / 3, GAME_TILESIZE / 3))
                self.image.fill(COLOR_GREEN)
                self.image.set_colorkey(COLOR_GREEN)
                self.extraGraphics = ExtraGraphics(self, self.game, "rotor_bullet", "center", GAME_WIDTH + 15, GAME_HEIGHT + 15)
                self.vel = vec(BULLET_ROTOR_SPEED, 0)

                # Sound
                self.game.snd_mob_rotor.stop()
                self.game.snd_mob_rotor.play()
            self.rect = self.image.get_rect()
            self.rect.center = self.pos

            self.vel = self.vel.rotate(-self.angle)

        elif (self.sprite.name == "mob boss"):
            if (self.sprite.bullet_name == "rotor"):
                self.bullet_name = "rotor"
                self.pos = vec(self.sprite.rect.centerx, self.sprite.rect.centery)
                offset = vec(self.sprite.rect.height / 2, 0)
                self.pos += offset.rotate(-self.angle)
                self.image = pg.Surface((GAME_TILESIZE / 3, GAME_TILESIZE / 3))
                self.image.fill(COLOR_GREEN)
                self.image.set_colorkey(COLOR_GREEN)
                self.rect = self.image.get_rect()
                self.extraGraphics = ExtraGraphics(self, self.game, "rotor_bullet", "center", self.rect.centerx, self.rect.centery)
                self.rect.center = self.pos
                self.vel = vec(BULLET_ROTOR_SPEED, 0)
                self.vel = self.vel.rotate(-self.angle)

                # Sound
                self.game.snd_mob_rotor.stop()
                self.game.snd_mob_rotor.play()
            elif (self.sprite.bullet_name == "gun"):
                self.bullet_name = "gun"
                self.pos = vec(self.sprite.gun.rect.centerx, self.sprite.gun.rect.centery)
                offset = vec((self.sprite.gun.rect.width / 2), 0)
                self.pos += offset.rotate(-self.angle)
                self.image = self.game.img_player_bullet
                self.rect = self.image.get_rect()
                self.rect.center = self.pos
                self.vel = vec(BULLET_GUARD_SPEED, 0)
                self.vel = self.vel.rotate(-self.angle)

                # Sound
                self.game.snd_bullet_coin.stop()
                self.game.snd_bullet_coin.play()

        else:  # "Head" mob
            self.image = self.game.img_head_bullet
            self.rect = self.image.get_rect()
            if (x > (GAME_WIDTH / 2)):
                self.vel = vec(-BULLET_HEAD_SPEED, 0)
                self.pos = vec(x - self.rect.width, y)
                self.rect.topleft = self.pos
            else:
                self.vel = vec(BULLET_HEAD_SPEED, 0)
                self.pos = vec(x, y)
                self.rect.topleft = self.pos

            self.game.snd_mob_head.stop()
            self.game.snd_mob_head.play()

        self.image.set_colorkey(COLOR_GREEN)

    def killSelf(self):
        if (self.sprite.name == "rotor"):
            self.extraGraphics.killSelf()
        if (self.sprite.name == "mob boss"):
            if (self.bullet_name == "rotor"):
                self.extraGraphics.killSelf()
        self.kill()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos

        if ((self.rect.x <= 0) or (self.rect.left >= GAME_WIDTH)):
            self.killSelf()
        elif ((self.rect.bottom <= 0) or (self.rect.y >= GAME_HEIGHT)):
            self.killSelf()


# For "laser" mob
class Laser(pg.sprite.Sprite):
    def __init__(self, sprite, game, x, y):
        self.sprite = sprite
        self.game = game
        self.name = "laser_laser"
        self.groups = self.game.grp_allSprites, self.game.grp_mobLasers  # Own laser grp ig
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_data(x, y)

    def load_data(self, x, y):
        self.image = pg.Surface((4, (GAME_HEIGHT - (GAME_TILESIZE * 2.5)) - y))
        self.image.fill(COLOR_LASER)
        self.rect = self.image.get_rect()
        if (self.sprite.name != "mob boss"):
            self.rect.midtop = (x, y)
        else:
            self.offset_x = x
            self.rect.topleft = (self.sprite.rect.x + self.offset_x, y)
        self.extraGraphics = ExtraGraphics(self, self.game, "laser", "midbottom", self.rect.centerx, self.rect.bottom)

    def killSelf(self):
        self.extraGraphics.killSelf()
        self.kill()

    def update(self):
        if (self.sprite.name != "mob boss"):
            self.rect.midtop = self.sprite.rect.midbottom
        else:
            self.rect.topleft = (self.sprite.rect.x + self.offset_x, self.sprite.rect.bottom)

        if (self.sprite.name != "mob boss"):
            if (not self.sprite.shooting):
                self.killSelf()
        else:
            if (not self.sprite.shooting_lasers):
                self.killSelf()


class Wall(pg.sprite.Sprite):
    def __init__(self, game, name, x, y, width, height):
        self.game = game
        self.name = name
        self.groups = self.game.grp_allSprites, self.game.grp_walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_data(x, y, width, height)

    def load_data(self, x, y, width, height):
        self.image = pg.Surface((width, height))
        self.image.fill(COLOR_GREEN)
        self.image.set_colorkey(COLOR_GREEN)  # Makes wall invisible
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def killSelf(self):
        self.kill()


class Shop(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.name = "shop"
        self.groups = self.game.grp_allSprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_data(x, y)

    def load_data(self, x, y):
        self.image = self.game.img_shop
        self.image.set_colorkey(COLOR_GREEN)
        self.rect = self.image.get_rect()
        self.rect.midbottom = ((x - (self.rect.width / 2)), y)

    def killSelf(self):
        self.kill()


class Button(pg.sprite.Sprite):
    def __init__(self, game, name, x, y, width, height):
        self.game = game
        self.name = name
        self.groups = self.game.grp_allSprites, self.game.grp_buttons
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_data(x, y, width, height)

    def load_data(self, x, y, width, height):
        self.image = pg.Surface((width, height))
        self.image.fill(COLOR_MOB_DARK)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def killSelf(self):
        self.kill()

    def update(self):
        mouse_x, mouse_y = pg.mouse.get_pos()

        if ((mouse_x >= self.rect.x) and (mouse_x <= (self.rect.x + self.rect.width))):
            if ((mouse_y >= self.rect.y) and (mouse_y <= (self.rect.y + self.rect.height))):
                self.image.fill(COLOR_MOB_LIGHT)
            else:
                self.image.fill(COLOR_MOB_DARK)
        else:
            self.image.fill(COLOR_MOB_DARK)

    def checkClick(self):
        mouse_x, mouse_y = pg.mouse.get_pos()

        if ((mouse_x >= self.rect.x) and (mouse_x <= (self.rect.x + self.rect.width))):
            if ((mouse_y >= self.rect.y) and (mouse_y <= (self.rect.y + self.rect.height))):
                if (self.name != "pause"):
                    if (self.name == "play"):
                        self.game.playing = True
                    elif (self.name == "main menu"):
                        self.game.playing = False
                    elif (self.name == "play again"):
                        self.game.playing = True
                        self.game.play_again = True
                    elif (self.name == "how to play"):
                        self.game.playing = False
                    elif (self.name == "quit"):
                        self.game.playing = False
                        self.game.running = False

                    self.game.waiting = False
                    if (self.name != "how to play"):
                        if (self.name != "play again"):
                            self.game.current_screen = "main"
                    else:
                        self.game.current_screen = "htp"
                else:
                    self.game.pause = not self.game.pause
                    self.game.kill_group(self.game.grp_buttons)
