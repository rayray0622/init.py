import pygame
import random
import os,sys
import serial, json
COM_PORT = 'COM6'
BRAUD_RATE = 9600
ser = serial.Serial(COM_PORT,BRAUD_RATE)
jx = 0
jy = 0
jz = 1
js = 1



FPS = 60 
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
YELLOW = (255,255,0)
WIDTH = 500
HEIGHT = 600
btn_state = 1
pre_state = 1
shoot_state = 1
btn_count = 0
def getjoystick():
    global jx,jy,js,jz,btn_state,pre_state,shoot_state,btn_count
    while ser.in_waiting:
        try:
            mcu_feedback = ser.readline().decode()
            print(mcu_feedback)
            j = json.loads(mcu_feedback)
            x = j['X']
            y = j['Y']
            z = j['Z']
            s = j['S']
            btn_state = j['S']
            js = 1
            if btn_state !=  pre_state:
                btn_count += 1
                if btn_count == 2:
                    js = 0
                    btn_count = 0
                else:
                    js = 1
            print("X:%d,Y:%d,Z:%d,S:%d"%(x,y,z,js))
            jx = x
            jy = y
            jz = z
            pre_state = btn_state

        except:
            print("error")

            


def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path,relative_path))

# 初始化遊戲 and 創建視窗
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("射擊遊戲")
clock = pygame.time.Clock()

shoot_sound = pygame.mixer.Sound(get_path("sound/shoot.wav"))
die_sound = pygame.mixer.Sound(get_path("sound/rumble.ogg"))
sheild_sound = pygame.mixer.Sound(get_path("sound/pow0.wav"))
gun_sound = pygame.mixer.Sound(get_path("sound/pow1.wav"))
expl_sounds = [
    pygame.mixer.Sound(get_path("sound/expl0.wav")),
    pygame.mixer.Sound(get_path("sound/expl1.wav"))
]
pygame.mixer.music.load(get_path("sound/background.ogg"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)                                     


background_img = pygame.image.load(get_path("img/background.png")).convert()
player_img = pygame.image.load(get_path("img/player.png")).convert()
player_mini_img = pygame.transform.scale(player_img,(25,19))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)


bullet_img = pygame.image.load(get_path("img/bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(get_path(f"img/rock{i}.png")).convert())

expl_anim = {}
expl_anim['lg'] = []
expl_anim['sm']  = []
power_img = {}
power_img['shield'] = pygame.image.load(get_path('img/shield.png')).convert()
power_img['gun'] = pygame.image.load(get_path('img/gun.png')).convert()
expl_anim['player'] = []
for i in range(9):
    expl_img = pygame.image.load(get_path(f"img/expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img,(75,75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img,(30,30)))
    player_expl_img = pygame.image.load(get_path(f"img/player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)

                           


font_name = get_path("font.ttf")
def draw_health(surf,hp,x,y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,GREEN,fill_rect)
    pygame.draw.rect(surf,WHITE,outline_rect,2)

def draw_lives(surf,lives,img,x,y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 32*i
        img_rect.y = y
        surf.blit(img,img_rect)
def draw_init():
    pygame.mixer.music.stop()
    background_img = pygame.image.load(get_path("img/background.png")).convert()
    screen.fill(BLACK)
    screen.blit(background_img,(0,0))
    draw_text(screen,'太空生存戰',64,WIDTH/2,HEIGHT/4)
    draw_text(screen,'←→移動飛船 空白建觸發射子彈~',22,WIDTH/2,HEIGHT/2 )
    draw_text(screen,'按住案件開始:', 18,WIDTH/2,HEIGHT*3/4)
    pygame.display.update()
    waiting = True

    while waiting:
        clock.tick(FPS)
        getjoystick()
        if jz == 0 or js == 0:
            waiting = False
            pygame.mixer.music.play(-1)
            return False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                pygame.mixer.music.play(-1)
                return False

    
def draw_text(surf,text,size,x,y):
    font = pygame.font.Font(font_name,size)
    text_surface = font.render(text,True,WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surf.blit(text_surface,text_rect)  

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.image = pygame.transform.scale(player_img,(50,38))
        self.image.set_colorkey(BLACK)
        self.radius = 20
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT-10
        self.speedx = 8
        self.health = 100
        self.gun = 1
        self.gun_time = 0
    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks() 

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now
        Key_pressed = pygame.key.get_pressed()
        if self.hidden and pygame.time.get_ticks()-self.hide_time > 1000:
           self.hidden = False
           self.rect.centerx = WIDTH/2
           self.rect.bottom = HEIGHT-10
           
       
        if Key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if Key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        if Key_pressed[pygame.K_UP]:
            self.rect.y -= self.speedx
        if Key_pressed[pygame.K_DOWN]:
            self.rect.y += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        elif self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > HEIGHT and self.hidden == False:
            self.rect.bottom = HEIGHT
        
    def shoot(self):
        if not (self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.top)
                bullet2 = Bullet(self.rect.right, self.rect.top)
                all_sprites.add(bullet1,bullet2)
                bullets.add(bullet1,bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2,HEIGHT+500)

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width/2*0.85)
        self.rect.x = random.randrange(0,WIDTH-self.rect.width)
        self.rect.y = random.randrange(-100,-40)
        self.speedy = random.randrange(2,10)
        self.speedx = random.randrange(-3,3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3,3)
    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0,WIDTH-self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedy = random.randrange(2,10)
            self.speedx = random.randrange(-3,3)
    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori,self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()
class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center
class Power(pygame.sprite.Sprite):
    def __init__(self,center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(('shield', 'gun'))
        self.image = power_img[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


        


running = True
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
rocks = pygame.sprite.Group()
for i in range(8):
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)
bullets = pygame.sprite.Group()
powers = pygame.sprite.Group()
score = 0 
show_int = True


while running:
    if show_int:
        close = draw_init()
        if close:
            break
        show_int = False
        all_sprites = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        rocks = pygame.sprite.Group()
        for i in range(8):
            r = Rock()
            all_sprites.add(r)
            rocks.add(r)
            bullets = pygame.sprite.Group()
            powers = pygame.sprite.Group()
        score = 0 
    clock.tick(FPS)

    # 取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running =False
        # 鍵盤移動
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
    if js == 0:
        player.shoot()
    player.rect.x += jx/10
    player.rect.y -= jy/10

    # 更新遊戲
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks,bullets,True,True)
    for hit in hits:
        score += 200//hit.radius
        expl = Explosion(hit.rect.center,'lg')
        all_sprites.add(expl)
        random.choice(expl_sounds).play()
        r = Rock()
        all_sprites.add(r)
        if random.random() > 0.5:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        rocks.add(r)
    hits = pygame.sprite.spritecollide(player,rocks,True,pygame.sprite.collide_circle)
    for hit in hits:
        player.health -= hit.radius
        expl = Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)
        r = Rock()
        all_sprites.add(r)
        rocks.add(r)
        if player.health <= 0:
            dealth_expl = Explosion(player.rect.center,'player')
            all_sprites.add(dealth_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
    if player.lives == 0 and not(dealth_expl.alive()):
        show_int = True
    hits = pygame.sprite.spritecollide(player,powers,True)
    for hit in hits:
        if hit.type == 'shield':
            sheild_sound.play()
            player.health += 20
            if player.health > 100:
                player.health = 100
        elif hit.type == 'gun':
            gun_sound.play()
            player.gunup()

    
    screen.fill(BLACK)
    screen.blit(background_img,(0,0))
    all_sprites.draw(screen)
    draw_text(screen,str(score),18,WIDTH/2,10)
    draw_health(screen,player.health,5,18)
    draw_lives(screen,player.lives,player_mini_img,WIDTH-100,15)
    pygame.display.update()
    getjoystick()
    
pygame.quit()
