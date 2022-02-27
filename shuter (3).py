from pygame import *
from random import *
import sqlite3
from pygame.sprite import Group
import pygame_menu
from pygame_menu.examples import create_example_window
from typing import Tuple, Any

font.init()
font = font.Font(None, 36)
score = 0
lose = 0
max_lose = 3
goal = 100
con = sqlite3.connect("mydatabase.sqlite")
cur = con.cursor()
record_score1 = 0


class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (80, 80))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def fire(self):
        bullet = Bullet("data/SpaceInvadersLaserDepiction.png", self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed + 10
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed + 10


class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lose
        # исчезает, если дойдет до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lose = lose + 1


class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:  # если координата пули по y меньше 0
            self.kill()


finish = False
win_width = 1200
win_height = 1000
window = display.set_mode((win_width, win_height))
ship = Player("data/SpaceInvadersLaserCannonDepiction.png", 5, win_height - 80, 80, 100, 5)
run = False
bullets = sprite.Group()
monsters: Group = sprite.Group()

for i in range(1, 6):
    monster = Enemy("data/SpaceInvadersAlienDepiction.png", 100, 80, 80, 50, randint(1, 5))
    monsters.add(monster)


def start_the_game() -> None:
    global run
    global record_score1
    global score
    global finish
    run = True
    while run:
        time.delay(50)
        for e in event.get():
            if e.type == QUIT:
                run = False
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    ship.fire()
        if not finish:
            collides = sprite.groupcollide(monsters, bullets, True, True)
            for c in collides:
                score = score + 1
                if score > 50:
                    monster1 = Enemy("data/SpaceInvadersAlienDepiction.png", randint(80, win_width - 80), -40, 80, 50,
                                     randint(6, 10))
                    monsters.add(monster1)
                elif score > 100:
                    monster1 = Enemy("data/SpaceInvadersAlienDepiction.png", randint(80, win_width - 80), -40, 80, 50,
                                     randint(10, 15))
                    monsters.add(monster1)
                else:
                    monster1 = Enemy("data/SpaceInvadersAlienDepiction.png", randint(80, win_width - 80), -40, 80, 50,
                                     randint(1, 5))
                    monsters.add(monster1)
            result = cur.execute("""SELECT record FROM pygame """).fetchall()
            for elem in result:
                record_score1 = elem[0]
            if record_score1 < score:
                cur.execute(f"""UPDATE pygame
                    SET record = {score}""")
                con.commit()
            result = cur.execute("""SELECT record FROM pygame """).fetchall()
            for elem in result:
                record_score1 = elem[0]
            window.fill((255, 255, 255))
            text = font.render("Счет: " + str(score), 1, (0, 0, 0))
            window.blit(text, (10, 20))
            text_lose = font.render("Пропущено: " + str(lose), 1, (0, 0, 0))
            window.blit(text_lose, (10, 50))
            text_record = font.render("Рекорд: " + str(record_score1), 1, (0, 0, 0))
            window.blit(text_record, (10, 80))
            bullets.update()
            bullets.draw(window)
            ship.update()
            ship.reset()
            monsters.update()
            monsters.draw(window)
            if sprite.spritecollide(ship, monsters, False) or lose >= max_lose:
                finish = True
                img = image.load('data/wasted.png')
                window.fill((255, 255, 255))
                window.blit(transform.scale(img, (win_width, win_height)), (0, 0))
        display.update()
    

def clear_record():
    cur.execute(f"""UPDATE pygame
                        SET record = 0""")
    con.commit()


surface = create_example_window('Example - Simple', (1200, 1000))
menu = pygame_menu.Menu(
    height=1000,
    theme=pygame_menu.themes.THEME_BLUE,
    title='Welcome',
    width=1200)
menu.add.button('Clear_record', clear_record)
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)

if __name__ == '__main__':
    menu.mainloop(surface)
