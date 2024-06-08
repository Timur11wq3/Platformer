import json
import pygame as pg
import pygame.mixer
import pytmx

pg.init()

SCREEN_WIDTH = 1680
SCREEN_HEIGHT = 1050
FPS = 80
TILE_SCALE = 2

GRAVITY = 2
MOVE_SPEED = 10
JUMP_SPEED = -40
MAX_FALL_SPEED = 20

font = pg.font.Font(None, 36)

pygame.mixer.music.load("music 2.mp3")
pygame.mixer.music.set_volume(0.1)


class Button:
    def __init__(self, text, x, y, width, height, font, bg_color, text_color):
        self.text = text
        self.rect = pg.Rect(x, y, width, height)
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.text_surf = font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        pg.draw.rect(screen, self.bg_color, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class Player(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super(Player, self).__init__()
        self.load_animations()
        self.current_animation = self.idle_animation_right
        self.image = self.current_animation[0]
        self.current_image = 0
        self.rect = self.image.get_rect()
        self.rect.center = (72, 832)
        self.is_paused = False

        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = GRAVITY
        self.is_jumping = False
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE

        self.timer = pg.time.get_ticks()
        self.interval = 300

        self.hp = 10
        self.damage_timer = pg.time.get_ticks()
        self.damage_interval = 1000

    def get_damage(self):
        if pg.time.get_ticks() - self.damage_timer > self.damage_interval:
            self.hp -= 3
            self.damage_timer = pg.time.get_ticks()

    def load_animations(self):
        tile_size = 32
        tile_scale = 4

        self.idle_animation_right = []

        num_images = 5
        spritesheet = pg.image.load("sprites/Sprite Pack 3/2 - Twiggy/Idle (32 x 32).png")

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.idle_animation_right.append(image)

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.move_animation_right = []

        num_images = 6
        spritesheet = pg.image.load("sprites/Sprite Pack 3/2 - Twiggy/Running (32 x 32).png")

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.move_animation_right.append(image)

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

    def update(self, platforms):
        if not self.is_paused:
            keys = pg.key.get_pressed()
            if keys[pg.K_SPACE] and not self.is_jumping:
                self.jump()

            if keys[pg.K_a]:
                self.velocity_x = -MOVE_SPEED
                self.switch_animation(self.move_animation_left)
            elif keys[pg.K_d]:
                self.velocity_x = MOVE_SPEED
                self.switch_animation(self.move_animation_right)
            else:
                self.velocity_x = 0
                self.switch_to_idle()

            self.rect.x += self.velocity_x
            self.handle_horizontal_collisions(platforms)

            self.velocity_y += self.gravity
            self.velocity_y = min(self.velocity_y, MAX_FALL_SPEED)
            self.rect.y += self.velocity_y
            self.is_jumping = True
            self.handle_vertical_collisions(platforms)

            self.animate()
            self.constrain_to_map()

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = JUMP_SPEED
            self.is_jumping = True

    def switch_animation(self, new_animation):
        if self.current_animation != new_animation:
            self.current_animation = new_animation
            self.current_image = 0

    def switch_to_idle(self):
        if self.current_animation in [self.move_animation_right, self.move_animation_left]:
            self.current_animation = self.idle_animation_right if self.current_animation == self.move_animation_right else self.idle_animation_left
            self.current_image = 0

    def handle_horizontal_collisions(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right

    def handle_vertical_collisions(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.is_jumping = False
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                self.velocity_y = 0

    def animate(self):
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image = (self.current_image + 1) % len(self.current_animation)
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()

    def constrain_to_map(self):
        self.rect.right = min(self.rect.right, self.map_width)
        self.rect.left = max(self.rect.left, 0)
        self.rect.bottom = min(self.rect.bottom, self.map_height)
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0

        if self.rect.right > 1760:
            self.rect.right = 1760 - 20




class Crab(pg.sprite.Sprite):
    CRAB_GRAVITY = 2
    CRAB_MOVE_SPEED = 2

    def __init__(self, map_width, map_height, start_pos, final_pos):
        super(Crab, self).__init__()
        self.load_animations()
        self.current_animation = self.animation
        self.image = self.current_animation[0]
        self.current_image = 0
        self.rect = self.image.get_rect()
        self.rect.bottomleft = start_pos
        self.left_edge = start_pos[0]
        self.right_edge = final_pos[0] + self.image.get_width()
        self.is_paused = False

        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = self.CRAB_GRAVITY
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE

        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.direction = "right"

    def load_animations(self):
        tile_scale = 4
        tile_size = 32
        self.animation = []
        image = pg.image.load("sprites/Sprite Pack 2/9 - Snip Snap Crab/Movement_(Flip_image_back_and_forth) (32 x 32).png")
        image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
        self.animation.append(image)
        self.animation.append(pg.transform.flip(image, True, False))

    def update(self, platforms):
        if not self.is_paused:
            if self.direction == "right":
                self.velocity_x = self.CRAB_MOVE_SPEED
                if self.rect.right >= self.right_edge:
                    self.direction = "left"
            elif self.direction == "left":
                self.velocity_x = -self.CRAB_MOVE_SPEED
                if self.rect.left <= self.left_edge:
                    self.direction = "right"

            self.rect.x += self.velocity_x
            self.rect.y += self.velocity_y + self.gravity

            self.handle_platform_collisions(platforms)
            self.animate()

    def handle_platform_collisions(self, platforms):
        for platform in platforms:
            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0

            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left

            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right

    def animate(self):
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()


class Pumpkin(Crab):
    PUMPKIN_MOVE_SPEED = 3

    def __init__(self, map_width, map_height, start_pos, final_pos):
        super(Pumpkin, self).__init__(map_width, map_height, start_pos, final_pos)
        self.velocity_x = self.PUMPKIN_MOVE_SPEED
        self.load_animations()
        self.rect = self.image.get_rect()
        self.rect.bottomleft = start_pos
        self.left_edge = start_pos[0]
        self.right_edge = final_pos[0] + self.image.get_width()

    def load_animations(self):
        tile_scale = 4
        tile_size = 16
        self.animation = []
        image = pg.image.load("sprites/Sprite Pack 2/4 - Robo Pumpkin/Standing (16 x 16).png")
        image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
        self.animation.append(image)
        self.animation.append(pg.transform.flip(image, True, False))


class Ball(pg.sprite.Sprite):
    BALL_SPEED = 10
    BALL_SIZE = (30, 30)

    def __init__(self, player_rect, direction):
        super(Ball, self).__init__()
        self.direction = direction
        self.speed = self.BALL_SPEED
        self.image = pg.image.load("sprites/ball.png")
        self.image = pg.transform.scale(self.image, self.BALL_SIZE)
        self.rect = self.image.get_rect()

        if direction == "right":
            self.rect.x = player_rect.right
        else:
            self.rect.x = player_rect.left - self.BALL_SIZE[0]
        self.rect.centery = player_rect.centery

    def update(self):
        if self.direction == "right":
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Platform(pg.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super(Platform, self).__init__()
        self.image = pg.transform.scale(image, (width * TILE_SCALE, height * TILE_SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SCALE
        self.rect.y = y * TILE_SCALE


class Coin(pg.sprite.Sprite):
    COIN_SIZE = (16, 16)
    COIN_SCALE = 4
    ANIMATION_INTERVAL = 200
    NUM_IMAGES = 4

    def __init__(self, x, y):
        super(Coin, self).__init__()
        self.load_animations()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.current_image = 0
        self.timer = pg.time.get_ticks()

    def load_animations(self):
        self.images = []
        spritesheet = pg.image.load("sprites/spr_coin_strip4.png")

        for i in range(self.NUM_IMAGES):
            image = spritesheet.subsurface((i * self.COIN_SIZE[0], 0, self.COIN_SIZE[0], self.COIN_SIZE[1]))
            image = pg.transform.scale(image,
                                       (self.COIN_SIZE[0] * self.COIN_SCALE, self.COIN_SIZE[1] * self.COIN_SCALE))
            self.images.append(image)

    def update(self):
        if pg.time.get_ticks() - self.timer > self.ANIMATION_INTERVAL:
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]
            self.timer = pg.time.get_ticks()


class Portal(pg.sprite.Sprite):
    COIN_SIZE = (64, 64)
    COIN_SCALE = 4
    ANIMATION_INTERVAL = 100
    NUM_IMAGES = 8

    def __init__(self, x, y):
        super(Portal, self).__init__()
        self.load_animations()
        self.image = self.images[0]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.current_image = 0
        self.timer = pg.time.get_ticks()

    def load_animations(self):
        self.images = []
        spritesheet = pg.image.load("sprites/Green Portal Sprite Sheet.png").convert_alpha()

        for i in range(self.NUM_IMAGES):
            image = spritesheet.subsurface((i * self.COIN_SIZE[0], 0, self.COIN_SIZE[0], self.COIN_SIZE[1]))
            image = pg.transform.scale(image,
                                       (self.COIN_SIZE[0] * self.COIN_SCALE, self.COIN_SIZE[1] * self.COIN_SCALE))
            self.images.append(image)

    def update(self):
        if pg.time.get_ticks() - self.timer > self.ANIMATION_INTERVAL:
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]
            self.timer = pg.time.get_ticks()


class Ship(pg.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super(Ship, self).__init__()
        self.image = pg.transform.scale(image, (width * TILE_SCALE, height * TILE_SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SCALE
        self.rect.y = y * TILE_SCALE


class Game:
    def __init__(self):
        pygame.mixer.music.play(-1)
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Платформер")
        self.level = 1
        self.clock = pg.time.Clock()
        self.is_running = True
        self.coins_score = 0
        self.camera_x = 0
        self.camera_y = 0
        self.background_menu = pg.image.load("menu.jpg")
        self.background_menu = pg.transform.scale(self.background_menu, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.is_play = False
        self.mode = "menu"
        self.is_paused = False
        self.font = font

        # Кнопки
        self.start_button = Button('Старт', SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50, self.font, (0, 255, 0), (0, 0, 0))
        self.exit_button = Button('Выход', SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50, self.font, (255, 0, 0), (0, 0, 0))
        self.continue_button = Button('Продолжить', SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50, self.font, (0, 255, 0), (0, 0, 0))

    def setup(self):
        self.coins_score = 0
        self.is_play = True
        self.mode = "game"
        self.is_paused = False
        self.background = pg.image.load("Background.png")
        self.background = pg.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.balls = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.portals = pg.sprite.Group()
        self.shipi = pg.sprite.Group()

        self.tmx_map = pytmx.load_pygame(f"maps/level{self.level}.tmx")
        self.load_map()

        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 4

    def load_map(self):
        self.map_pixel_width = self.tmx_map.width * self.tmx_map.tilewidth * TILE_SCALE
        self.map_pixel_height = self.tmx_map.height * self.tmx_map.tileheight * TILE_SCALE

        load_portal = False

        for layer in self.tmx_map:
            if layer.name == "Game":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        platform = Platform(tile, x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                            self.tmx_map.tilewidth, self.tmx_map.tileheight)
                        self.all_sprites.add(platform)
                        self.platforms.add(platform)


                with open(f"maps/level{self.level}_enemies.json", "r") as json_file:
                    data = json.load(json_file)

                for enemy in data["enemies"]:
                    if enemy["name"] == "Crab":

                        x1 = enemy["start_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                        y1 = enemy["start_pos"][1] * TILE_SCALE * self.tmx_map.tileheight

                        x2 = enemy["final_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                        y2 = enemy["final_pos"][1] * TILE_SCALE * self.tmx_map.tileheight


                        crab = Crab(self.map_pixel_width, self.map_pixel_height, [x1, y1], [x2, y2])
                        self.all_sprites.add(crab)
                        self.enemies.add(crab)
                    elif enemy["name"] == "Pumpkin":
                        x1 = enemy["start_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                        y1 = enemy["start_pos"][1] * TILE_SCALE * self.tmx_map.tileheight

                        x2 = enemy["final_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                        y2 = enemy["final_pos"][1] * TILE_SCALE * self.tmx_map.tileheight
                        pumpkin = Pumpkin(self.map_pixel_width, self.map_pixel_height, [x1, y1], [x2, y2])
                        self.all_sprites.add(pumpkin)
                        self.enemies.add(pumpkin)

            elif layer.name == "Coins":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        coin = Coin(x * self.tmx_map.tilewidth * TILE_SCALE,
                                    y * self.tmx_map.tileheight * TILE_SCALE)
                        self.all_sprites.add(coin)
                        self.coins.add(coin)
                self.coins_amount = len(self.coins.sprites())
            elif layer.name == "Portals":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        portal = Portal(x * self.tmx_map.tilewidth * TILE_SCALE, y * self.tmx_map.tileheight * TILE_SCALE)
                        self.all_sprites.add(portal)
                        self.portals.add(portal)
                        load_portal = True
                        break
            elif layer.name == "Shipi":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        ship = Ship(tile, x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                    self.tmx_map.tilewidth, self.tmx_map.tileheight)
                        self.all_sprites.add(ship)
                        self.shipi.add(ship)

        self.player = Player(self.map_pixel_width, self.map_pixel_height)
        self.all_sprites.add(self.player)

        # self.crab = Crab(self.map_pixel_width, self.map_pixel_height)
        # self.all_sprites.add(self.crab)
        # self.enemies.add(self.crab)

        # self.pumpkin = Pumpkin(self.map_pixel_width, self.map_pixel_height)
        # self.all_sprites.add(self.pumpkin)
        # self.enemies.add(self.pumpkin)

        for layer in self.tmx_map:
            if layer.name == "Game":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        platform = Platform(tile, x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                            self.tmx_map.tilewidth, self.tmx_map.tileheight)
                        self.all_sprites.add(platform)
                        self.platforms.add(platform)
            elif layer.name == "Coins":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        coin = Coin(x * self.tmx_map.tilewidth * TILE_SCALE, y * self.tmx_map.tileheight * TILE_SCALE)
                        self.all_sprites.add(coin)
                        self.coins.add(coin)

        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 4

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN and self.mode == "game":
                    if self.player.current_animation in (self.player.idle_animation_right, self.player.move_animation_right):
                        direction = "right"
                    else:
                        direction = "left"
                    ball = Ball(self.player.rect, direction)
                    self.balls.add(ball)
                    self.all_sprites.add(ball)
                if event.key == pg.K_p or event.key == pg.K_ESCAPE:
                    if self.mode == "game":
                        self.is_paused = not self.is_paused
                        if self.is_paused:
                            self.mode = "pause"
                        else:
                            self.mode = "game"
                    elif self.mode == "pause":
                        self.is_paused = False
                        self.mode = "game"
                if event.key == pg.K_ESCAPE and self.mode == "menu":
                    self.is_running = False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                if self.mode == "menu":
                    if self.start_button.is_clicked(mouse_pos):
                        self.setup()
                    if self.exit_button.is_clicked(mouse_pos):
                        self.is_running = False
                elif self.mode == "pause":
                    if self.continue_button.is_clicked(mouse_pos):
                        self.is_paused = False
                        self.mode = "game"
                    if self.exit_button.is_clicked(mouse_pos):
                        self.is_running = False

    def update_camera(self):
        target_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        target_y = self.player.rect.centery - SCREEN_HEIGHT // 2
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        self.camera_x = max(0, min(self.camera_x, self.map_pixel_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.map_pixel_height - SCREEN_HEIGHT))

    def update(self):
        if self.mode != "game":
            return

        if self.player.hp <= 0:
            self.mode = "game over"
            return

        for sprite in self.all_sprites:
            if isinstance(sprite, Player) or isinstance(sprite, Crab):
                sprite.update(platforms=self.platforms)
            else:
                sprite.update()

        for enemy in self.enemies.sprites():
            if pg.sprite.collide_mask(self.player, enemy):
                self.player.get_damage()

        for ship in self.shipi.sprites():
            if pg.sprite.collide_mask(self.player, ship):
                self.player.get_damage()

        pg.sprite.groupcollide(self.balls, self.enemies, True, True)
        pg.sprite.groupcollide(self.balls, self.platforms, True, False)

        coins_collected = pg.sprite.spritecollide(self.player, self.coins, True)
        portals_collected = pg.sprite.spritecollide(self.player, self.portals, False, pg.sprite.collide_mask)

        if coins_collected:
            self.coins_score += 1

        if portals_collected and self.coins_score > self.coins_amount // 2:
            self.level += 1
            if self.level == 4:
                quit()
            self.setup()
        self.update_camera()

    def draw(self):
        if self.mode == "menu":
            self.screen.blit(self.background_menu, (0, 0))
            self.draw_text("Меню", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
            self.start_button.draw(self.screen)
            self.exit_button.draw(self.screen)
        elif self.mode == "pause":
            self.screen.blit(self.background_menu, (0, 0))
            self.draw_text("Пауза", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
            self.continue_button.draw(self.screen)
            self.exit_button.draw(self.screen)
        else:
            self.screen.fill("light blue")
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))

            hp_bar_length = 100
            hp_bar_height = 20
            current_hp_length = hp_bar_length * (self.player.hp / 10)
            hp_bar_color = (255, 0, 0)
            pg.draw.rect(self.screen, hp_bar_color, (10, 10, current_hp_length, hp_bar_height))
            pg.draw.rect(self.screen, pg.Color("black"), (10, 10, hp_bar_length, hp_bar_height), 2)

            if self.mode == "game over":
                text = font.render("Вы проиграли", True, (255, 0, 0))
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(text, text_rect)

            coins_score_text = font.render(f"Coins: {self.coins_score}", True, "black")
            self.screen.blit(coins_score_text, (10, 30))

        pg.display.flip()

    def draw_text(self, text, size, x, y):
        font = pg.font.Font(None, size)
        text_surface = font.render(text, True, pg.Color("black"))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def main_menu(self):
        self.mode = "menu"

    def pause_menu(self):
        self.mode = "pause"

    def run(self):
        self.main_menu()
        while self.is_running:
            self.event()
            if self.mode == "game":
                self.update()
            self.draw()
            self.clock.tick(FPS)
        pg.quit()
        quit()





if __name__ == "__main__":
    game = Game()
    game.run()
