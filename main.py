import pyglet
import random
import math
from pyglet.window import mouse
from time import sleep

import player as Player
import projectile as Projectile
import enemy as Enemy
import hud as Hud
import particles as Particle


window = pyglet.window.Window(width=720, height=500)

# load images
img_player = pyglet.image.load_animation('assets/doge.gif')
doge_bin = pyglet.image.atlas.TextureBin()
# credits to u/red_white_blue on reddit
# https://www.reddit.com/r/dogecoin/comments/1ycffo/im_working_on_an_animated_web_banner_for_doge/
img_player.add_to_texture_bin(doge_bin)
img_bullet = pyglet.image.load('assets/heart.png')
# credits to xquatrox on deviantart
# https://www.deviantart.com/xquatrox/art/8-Bit-heart-stock-287592934
img_enemy_1 = pyglet.image.load('assets/chocolate_28px.png')
# credits to shutterstock
# https://www.shutterstock.com/image-vector/chocolate-bar-icon-pixel-art-flat-767821939
img_enemy_3 = pyglet.image.load('assets/evil_nyan_cat.png')
# credits to frostyplayz on deviantart
# https://www.deviantart.com/frostyplayz/art/EVIL-NYAN-CAT-568344463
img_background = pyglet.image.load_animation('assets/plain_space_bg.gif')
bg_bin = pyglet.image.atlas.TextureBin()
img_background.add_to_texture_bin(bg_bin)
img_background_sprite = pyglet.sprite.Sprite(img_background)

# load sfx
gun_sfx = pyglet.resource.media('assets/gun_44mag_11.wav', streaming=False)
gun_sfx.play()
hit_sfx = pyglet.resource.media('assets/explosion_x.wav', streaming=False)
# credits to wavsource
# http://www.wavsource.com/sfx/sfx2.htm

# Set sprites
Player.set_img(img_player)
Enemy.set_img([img_enemy_1, img_enemy_1, img_enemy_3])
Projectile.set_img(img_bullet)

# load high score
global high_score
fin = open("top.dat")
high_score = int(fin.read())

# mouse
mouse_position = [0, 0]


step = 0					# 30 steps == 1s

player = Player.add(mouse_position)
lives = 3
score = 0

phase = 0

'''
    Phase 0 - Game Menu
    Phase 1 - Play
    Phase 2 - Game Over Screen
    Phase 3 - High Scores
'''


def check_collision():
    global lives, score, hit_sfx
    player_position = player["sprite"].position

    # checks for collision between enemy sprite and player sprite
    for e in Enemy.Enemies:
        enemy_position = e["sprite"].position
        distance = (player_position[0] - enemy_position[0])**2 + (player_position[1] - enemy_position[1])**2
        
        if distance < 50**2:
            if not e["boss"]:
                if distance < 30**2:
                    hit_sfx.play()
                    Enemy.Enemies.remove(e)   # delete self
                    if not(player["immune"]):
                        player["immune"] = True
                        Player.counter = 0
                        lives -= 1
                    Particle.new_particle_system_dog(player_position)
            else:
                hit_sfx.play()
                e["target"] = (500, 220)
                if not(player["immune"]):
                    player["immune"] = True
                    Player.counter = 0
                    lives -= 1
                Particle.new_particle_system_dog(player_position)

    # checks for collision between enemy sprite and projectiles
    for heart in Projectile.Projectiles:
        heart_position = heart["sprite"].position

        for chocolate in Enemy.Enemies:
            enemy_position = chocolate["sprite"].position
            distance = (heart_position[0] - enemy_position[0])**2 + (heart_position[1] - enemy_position[1])**2

            if distance < 30**2:
                if not chocolate["boss"]:
                    Enemy.Enemies.remove(chocolate)  # delete enemy
                    score += 2
                else:
                    chocolate["sprite"].color = (255, 0, 0)
                    chocolate["lives"] -= 1
                if chocolate["boss"]:
                    if chocolate["lives"] == 0:
                        Enemy.Enemies.remove(chocolate)
                        score += 100
                Particle.new_particle_system(heart_position)
                Projectile.Projectiles.remove(heart)  # delete projectile
                break


def free_memory():

    for e in Enemy.Enemies:
        if e["sprite"].position[0] < 0:
            Enemy.Enemies.remove(e)
    for p in Projectile.Projectiles:
        if p["sprite"].position[0] > window.width:
            Projectile.Projectiles.remove(p)


def spawn_enemy():
    global step
    if step == 30 * 60:  # 15 def
            Enemy.add(random.randint(2, 2))
    elif step >= (60*60) and step % (60 * 60) == 1:  # 15 def
            Enemy.add(random.randint(2, 2))
    elif step % (max(9-math.floor(step/(10*30)), 4) if step < 90*60 else 2) == 0:

        if step < 5 * 60:
            Enemy.add(0)		                # Normal not curve
        elif step < 10 * 60:
            Enemy.add(random.randint(0, 1))		# Normal curve or not
        else:
            Enemy.add(random.randint(0, 1))                     # normal


def update_phase_0(dt):
    ...


def update_phase_1(dt):
    global phase, step, score, lives
    
    spawn_enemy()

    Player.update(dt)
    Enemy.update(dt, player)
    Projectile.update(dt)
    Particle.update(dt,player)

    check_collision()
    free_memory()

    if lives <= 0:
        sleep(2)
        goto_phase(2)

    score += 0.1
    step += 1


def update_phase_2(dt):
    ...


def update(dt):

    if phase == 0:
        update_phase_0(dt)
    elif phase == 1:
        update_phase_1(dt)
    else:
        update_phase_2(dt)

    Hud.update(phase, dt, lives, score, mouse_position, goto_phase, high_score)


def goto_phase(p):
    global phase, score, high_score, lives, step

    if p == 1:
        score = 0 
        lives = 3
        step = 0

    if p == 2:

        # destroy instances

        for i in Projectile.Projectiles:
            Projectile.Projectiles.remove(i)
        
        Projectile.Projectiles = []

        for i in Enemy.Enemies:
            Enemy.Enemies.remove(i)

        Enemy.Enemies = []

        for i in Particle.Particles:
            Particle.Particles.remove(i)
        Particle.Particles = []

        if score > high_score:
            f = open("top.dat", "w")
            f.write(str(math.floor(score)))
            high_score = score
    if p == 4:
        pyglet.clock.unschedule(update)
        pyglet.app.exit()

    sleep(0.1)
    phase = p


@window.event
def on_mouse_motion(x, y, dx, dy):
    mouse_position[0] = x
    mouse_position[1] = y


@window.event
def on_mouse_press(x, y, button, modifiers):
    global phase, gun_sfx

    if button == mouse.LEFT:
        Hud.on_mouse_press()
        if phase == 1:
            Projectile.new_projectile(player) 
            gun_sfx.play()


@window.event
def on_mouse_release(x, y, button, modifiers):
    
    if button == mouse.LEFT:
        Hud.on_mouse_release()


@window.event
def on_draw():
    global phase
    window.clear()

    if phase == 0:
        ...
    elif phase == 1:
        img_background_sprite.draw()
        Projectile.draw()
        Player.draw()
        Enemy.draw()
        Particle.draw()
    else:
        ...

    Hud.draw(phase)


pyglet.clock.schedule_interval(update, 1/60) 			# update every 1/60 s , i.e. run @ 60 fps

pyglet.app.run()
