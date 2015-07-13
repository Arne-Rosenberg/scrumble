#!/usr/bin/env python

import random, os.path

#import basic pygame modules
import pygame
from pygame.locals import *

#see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


###########################################game constants
MAX_SHOTS      = 6      #most player bullets onscreen-- standard 6
ALIEN_ODDS     = 22     #chances a new alien appears-- standard 22
BOMB_ODDS      = 60    #chances a new bomb will drop-- standard 60
ALIEN_RELOAD   = 12     #frames between new aliens-- standard 12
SCREENRECT     = Rect(0, 0, 1280, 700)  #standard (0,0,1280,700) 
SCORE          = 0

#########################################other vars

bossgeschafftvalue = 0

###################################################

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert_alpha()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


class dummysound:
    def play(self): pass

def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()



# each type of game object gets an init and an
# update function. the update function is called
# once per frame, and it is when each object should
# change it's current position and state. the Player
# object actually gets a "move" function instead of
# update, since it is passed extra information about
# the keyboard


class Player(pygame.sprite.Sprite):
    speed = 10
    bounce = 24
    gun_offset = -11
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midleft)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1
        #collisonmask
        self.mask=pygame.mask.from_surface(load_image('raumschiffmask.png'))
        
    def movey(self, directiony):
        self.rect.move_ip(0,directiony*self.speed)
        
    def move(self, directionx):
        #if directionx: 
        #    self.facing = directionx
        self.rect.move_ip(directionx*self.speed, 0)
        if self.rect.centerx > SCREENRECT.centerx:
            self.rect.centerx =  SCREENRECT.centerx
        self.rect = self.rect.clamp(SCREENRECT)
        #if directionx > 0:
         #   self.image = self.images[0]
        #elif directionx < 0:
            #self.image = self.images[1]
        #self.rect.top = self.origtop - (self.rect.left//self.bounce%2)

    def gunpos(self):
        #pos = self.facing*self.gun_offset + self.rect.centerx
        pos= self.rect.center
        return self.rect.center


class Alien(pygame.sprite.Sprite):
    speed = 5
    animcycle = 12
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.y=random.randint(0,SCREENRECT.height-self.rect.height)
        self.rect.top=self.y
        #self.facing = random.choice((-1,1)) * Alien.speed
        self.facing = -1*Alien.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            #self.facing = -self.facing;
            #self.rect.top = self.rect.bottom + 1
            #self.rect = self.rect.clamp(SCREENRECT)
            self.kill()
        self.frame = self.frame + 1
        self.image = self.images[self.frame//self.animcycle%3]

class Boss1(pygame.sprite.Sprite):
    animcycle = 16
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.y=random.randint(0,SCREENRECT.height-self.rect.height)
        self.rect.centerx=SCREENRECT.width-130
        self.rect.centery=self.y
        #self.facing = random.choice((-1,1)) * Alien.speed
        #self.facing = -1*Alien.speed
        self.frame = 0
        self.speedy=random.choice((-3,-2,-1,1,2,3))
        self.speedx= 0
        #if self.facing < 0:
            #self.rect.right = SCREENRECT.right

    def treffer(self):
		pass
		
    def update(self):
        #self.speedy=random.choice((-3,-2,-1,0,0,1,2,))
        self.rect.move_ip(self.speedx,self.speedy)
        if self.rect.centery< 0:
            self.rect.centery=0
            self.speedy= random.randint(1,3)
        if self.rect.centery >SCREENRECT.height:
            self.rect.centery=SCREENRECT.height
            self.speedy= random.randint(-3,-1)
        #if not SCREENRECT.contains(self.rect):
            #self.facing = -self.facing;
            #self.rect.top = self.rect.bottom + 1
            #self.rect = self.rect.clamp(SCREENRECT)
            #self.kill()
        self.frame = self.frame + 1
        self.image = self.images[self.frame//self.animcycle%4]
        
class Herz(pygame.sprite.Sprite):
    animcycle = 8
    images = []
    def __init__(self,myboss):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.myboss=myboss
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center=myboss.rect.center
        self.hitpoints=6
        self.frame=1
           
    def treffer(self):
        self.hitpoints-=1
        pygame.font.init()
        if self.hitpoints<=0:
            self.myboss.kill()
            self.kill()
            global SCORE
            SCORE = SCORE+1000
            global bossgeschafftvalue
            bossgeschafftvalue = 1
                        
        else:
            self.image=self.images[6-self.hitpoints]
            self.rect = self.image.get_rect()
            self.rect.center = self.myboss.rect.center
        
    def update(self):
        self.rect.center=self.myboss.rect.center
        self.frame = self.frame + 1
        self.herznummer = self.frame//self.animcycle%4  # zw 0 und 3
        if self.herznummer == 0:
            self.image=self.images[6-self.hitpoints]
            self.rect = self.image.get_rect()
            self.rect.center = self.myboss.rect.center
        elif self.herznummer == 1:
            self.image=self.images[6-self.hitpoints]
            self.image=pygame.transform.rotozoom(self.image,0.0,1.5)
            self.rect = self.image.get_rect()
            self.rect.center = self.myboss.rect.center
        elif self.herznummer == 2:
            self.image=self.images[6-self.hitpoints]
            self.image=pygame.transform.rotozoom(self.image,0.0,2.0)
            self.rect = self.image.get_rect()
            self.rect.center = self.myboss.rect.center
        elif self.herznummer == 3:
            self.image=self.images[6-self.hitpoints]
            self.image=pygame.transform.rotozoom(self.image,0.0,1.3)
            self.rect = self.image.get_rect()
            self.rect.center = self.myboss.rect.center




class LevelCount(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.font = pygame.font.Font(None, 60)
		self.update()
		self.rect = self.image.get_rect().move(350,640)
		self.font.set_bold(1)
		
	def update(self):
		global bossgeschafftvalue
		if bossgeschafftvalue == 1:
			self.bossgestorbenvar = "LEVEL 1 COMPLETE!!!!!"
			self.image = self.font.render(self.bossgestorbenvar, True, (255,255,255))
			print ("This works")





class Explosion(pygame.sprite.Sprite):
    defaultlife = 16
    animcycle = 4
    images = []
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life//self.animcycle%4]
        if self.life <= 0: self.kill()


class Shot(pygame.sprite.Sprite):
    speed = 13
    images = []
    animcycle= 2
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        #self.rect.center=pos
        self.frame=1 

    def update(self):
        self.rect.move_ip(self.speed,0)
        if self.rect.right >= SCREENRECT.width:
            self.kill()
        self.frame+=1
        self.image = self.images[self.frame//self.animcycle%2]

class Bomb(pygame.sprite.Sprite):
    #speed = -6
    images = []
    def __init__(self, alien):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.speedx= random.randint(-9,-3)
        self.speedy= random.randint(-1,1)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=
                    alien.rect.move(0,5).midbottom)

    def update(self):
        self.rect.move_ip(self.speedx,self.speedy)
        #if self.rect.bottom >= 470:
        if not SCREENRECT.contains(self.rect):
            Explosion(self)
            self.kill()


class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 40)
        self.font.set_italic(1)
        self.color = Color('white')
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(20,20)

    def update(self):
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, True, self.color)



def main(winstyle = 0):
    
    #var -------------------------
    
    global bossgeschafftvalue
    bossgeschafftvalue = 0

    #var--------------------------
    
    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print ('Warning, no sound')
        pygame.mixer = None

    # ------------------------------------------------------------Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    clock = pygame.time.Clock()
    
    #---------------------------------------------------------Load images, assign to sprite classes
    #-----------------------------------------(do this before the classes are used, after screen setup)
    img = load_image('raumschiff.png')
    Player.images = [img, pygame.transform.flip(img, 1, 0)]
    Explosion.images = load_images('hertzexplosion1.png','hertzexplosion2.png','hertzexplosion3.png','hertzexplosion4.png')
    Alien.images = load_images('monster1.png', 'monster2.png', 'monster3.png')
    Bomb.images = [load_image('tnt.png')]
    Shot.images = load_images('kugel3.png','kugel2.png')
    Boss1.images = load_images('gehirn1.png','gehirn2.png','gehirn3.png','gehirn4.png')
    #-----------------------------------------------------------------------------------------------decorate the game window
    icon = pygame.transform.scale(Alien.images[0], (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Pygame Aliens')
    pygame.mouse.set_visible(0)
    Herz.images=load_images('herz1.png','herz2.png','herz3.png','herz4.png','herz5.png','herz6.png')

    #-------------------------------------------------------------------create the background, tile the bgd image
    bgdtile = load_image('space2.jpeg')
    background = pygame.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0,0))
    pygame.display.flip()

    #-------------------------------------------------------------------------------load the sound effects
    boom_sound = load_sound('boom.wav')
    shoot_sound = load_sound('car_door.wav')
    if pygame.mixer:
        music = os.path.join(main_dir, 'data', 'Naph - Sapphire.wav')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

    #----------------------------------------------------------------------------------- Initialize Game Groups
    aliens = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    lastalien = pygame.sprite.GroupSingle()
    bosse = pygame.sprite.Group()

    #--------------------------------------------------------assign default groups to each sprite class
    Player.containers = all
    Alien.containers = aliens, all, lastalien
    Shot.containers = shots, all
    Bomb.containers = bombs, all
    Explosion.containers = all
    Score.containers = all
    LevelCount.containers = all
    Boss1.containers= bosse, all
    Herz.containers= bosse,all

    #-------------------------------------------------------------------Create Some Starting Values
    global score
    alienreload = ALIEN_RELOAD
    kills = 0
    clock = pygame.time.Clock()

    #-------------------------------------------------------------initialize our starting sprites
    global SCORE
    player = Player()
    Alien() #note, this 'lives' because it goes into a sprite group
    if pygame.font:
        all.add(Score())

    playtime = 0.0
    growingvalue = 0
    
    
    ################################ GAME STARTS #######################################
    
    while player.alive(): 

        milliseconds = clock.tick(60) #fps
        playtime += milliseconds / 1000.0
        growingvalue = growingvalue + 1 
        
        if growingvalue == 8:
			growingvalue = 0
			SCORE = SCORE + 1
			
                   
        if playtime > 5 and len(bosse) < 1 and bossgeschafftvalue == 0 and SCORE > 1000:
			Herz(Boss1())
			

            
        #------------------------------------------------------------------------get input
        for event in pygame.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
        keystate = pygame.key.get_pressed()

        #------------------------------------------------------------------ clear/erase the last drawn sprites
        all.clear(screen, background)

        #-------------------------------------------------------------------update all the sprites
        
        all.update()

        #---------------------------------------------------------------------handle player input
        directionx = keystate[K_RIGHT] - keystate[K_LEFT]
        player.move(directionx)
        directiony = keystate[K_DOWN] - keystate[K_UP]
        player.movey(directiony)
        firing = keystate[K_SPACE]
        
        if not player.reloading and firing and len(shots) < MAX_SHOTS:
            Shot(player.gunpos())
            shoot_sound.play()
        player.reloading = firing

        #-------------------------------------------------------------------- Create new alien
        if alienreload:
            alienreload = alienreload - 1
        elif not int(random.random() * ALIEN_ODDS):
            Alien()
            alienreload = ALIEN_RELOAD

        #--------------------------------------------------------------------------- Drop bombs
        if lastalien and not int(random.random() * BOMB_ODDS):
            Bomb(lastalien.sprite)

        #------------------------------------------------------------------------------ Detect collisions
        #for alien in pygame.sprite.spritecollide(player, aliens, 1):
        for alien in aliens :
            
            crashgroup = pygame.sprite.spritecollide(player,aliens, False, pygame.sprite.collide_mask)
            for crashalien in crashgroup :
                boom_sound.play()
                crashalien.kill()
                Explosion(crashalien)
                Explosion(player)
                SCORE = SCORE + 1
                player.kill()

        for alien in pygame.sprite.groupcollide(shots, aliens, 1, 1).keys():
            boom_sound.play()
            Explosion(alien)
            SCORE = SCORE + 50
        
        for bomb in bombs :
            
            crashgroup = pygame.sprite.spritecollide(player,bombs, False, pygame.sprite.collide_mask)
            for crashbomb in crashgroup :
                boom_sound.play()
                crashbomb.kill()
                Explosion(crashbomb)
                Explosion(player)
                #SCORE = SCORE + 1
                player.kill()

        #for bomb in pygame.sprite.spritecollide(player, bombs, 1):
        #    boom_sound.play()
        #    Explosion(player)
        #    Explosion(bomb)
        #    player.kill()
        
        for shot in pygame.sprite.groupcollide(shots, bombs, 1,1):
            boom_sound.play()
            Explosion(shot)
            SCORE= SCORE +100
            
        for shot in shots:
            for boss in bosse:
                 crashgroup = pygame.sprite.spritecollide(boss,shots, True, pygame.sprite.collide_mask)
                 for crashshot in crashgroup:
                     Explosion(crashshot)
                     boss.treffer()    
        #-----------------------------------------------------------------------draw the scene
        dirty = all.draw(screen)
        pygame.display.update(dirty)

        #-------------------------------------------------------------------------cap the framerate
        clock.tick(40)
    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    pygame.time.wait(1000)
    pygame.quit()



if __name__ == '__main__': main()
