import pygame
import time
import random
import os
WIDTH,HEIGHT=800,660
WIN=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("FlappyBird")
PATH_DIR=os.path.dirname(os.path.abspath(__file__))
BG=pygame.transform.scale(pygame.image.load(os.path.join(PATH_DIR, "assets", "background-day.png")), (WIDTH, HEIGHT))
BASE=pygame.transform.scale(pygame.image.load(os.path.join(PATH_DIR, "assets", "base.png")),(WIDTH, 112))
BIRD_DOWN_FLAP=pygame.transform.scale(pygame.image.load(os.path.join(PATH_DIR, "assets", "yellowbird-downflap.png")).convert_alpha(), (50,40))
BIRD_MID_FLAP=pygame.transform.scale(pygame.image.load(os.path.join(PATH_DIR, "assets", "yellowbird-midflap.png")).convert_alpha(), (50,40))
BIRD_UP_FLAP=pygame.transform.scale(pygame.image.load(os.path.join(PATH_DIR, "assets", "yellowbird-upflap.png")).convert_alpha(), (50,40))
GAME_OVER_TEXT=pygame.transform.scale_by(pygame.image.load(os.path.join(PATH_DIR, "assets", "gameover.png")).convert_alpha(), 1.8)
GREEN_PIPE=pygame.transform.scale(pygame.image.load(os.path.join(PATH_DIR, "assets", "pipe-green.png")).convert_alpha(),(70,420)) 
FLIPPED_GREEN_PIPE=pygame.transform.flip(GREEN_PIPE, False, True)
FPS=60
PIPE_SPEED=4
SCORE_IMAGE=[]
for i in range(10):
    path=os.path.join(PATH_DIR, "assets", str(i)+".png")
    IMAGE=pygame.transform.scale_by(pygame.image.load(path), 1.5)
    SCORE_IMAGE.append(IMAGE)
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        self.image=pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect=self.image.get_rect(topleft=(x,y))
    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))
class Base(Object):
    def __init__(self, x , y, width,height, image):
        super().__init__(x,y,width, height)
        self.image.blit(image, (0,0))
        self.mask=pygame.mask.from_surface(self.image)        
class Pipes(Object):
    def __init__(self, x, y, width, height, image, flipped=False):
        super().__init__(x, y, width, height)
        self.image.blit(image,(0,0))
        self.mask=pygame.mask.from_surface(self.image)
        self.passed=False       #To check if the bird has passed through the pipes successfully
        self.flipped=flipped
    def move(self, vel):
        self.rect.x-=vel
        
class Player(pygame.sprite.Sprite):
    IMAGES=[BIRD_DOWN_FLAP, BIRD_MID_FLAP, BIRD_UP_FLAP]
    ANIMATION_DELAY=4
    GRAVITY=0.5
    def __init__(self, x, y, width, height):
        self.rect=pygame.Rect(x, y, width, height)
        self.image=pygame.Surface((width, height), pygame.SRCALPHA)
        self.animation_count=0
        self.fall_count=0
        self.vel_y=0
    def update_image(self):
        index=(self.animation_count//self.ANIMATION_DELAY)%len(self.IMAGES)
        self.image.blit(self.IMAGES[index], (0,0))
        self.mask=pygame.mask.from_surface(self.image)
        self.animation_count+=1
        if self.animation_count>12:
            self.animation_count=0
    def gravity(self,fps):
        self.vel_y+=(self.GRAVITY/fps)*self.fall_count
        self.fall_count+=1
    def move_player(self,fps):
        self.gravity(fps)
        self.rect.y+=self.vel_y
        self.update_image()
    def jump(self,fps):
        self.fall_count=0
        self.vel_y=-self.GRAVITY*300/fps
    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))
def collision_base(obj1, obj2):
    return pygame.sprite.collide_mask(obj1, obj2)
def collision_pipes(player, objs):
    for obj in objs:
        if pygame.sprite.collide_mask(player, obj):
            return True
def draw_window(base, player, pipes, score):
    WIN.blit(BG, (0,0))
    for pipe in pipes:
        pipe.draw(WIN)
    base.draw(WIN)
    player.draw(WIN)
    req_score_images=[SCORE_IMAGE[int(i)] for i in list(str(score))]
    total_width=sum(image.get_width() for image in req_score_images)
    score_surface=pygame.Surface((total_width, req_score_images[0].get_height()), pygame.SRCALPHA)
    offset_x=0
    for i in range(len(req_score_images)):
        score_surface.blit(req_score_images[i], (offset_x,0))
        offset_x+=req_score_images[i].get_width()
    WIN.blit(score_surface, (WIDTH/2 - score_surface.get_width()/2, 25))
    pygame.display.update()
def main():
    run=True
    base=Base(0,HEIGHT-BASE.get_height(), *BASE.get_size(), BASE)
    player=Player(200, 200, 50, 40)
    pipes=[]
    delay=0
    clock=pygame.time.Clock()
    score=0
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
                break
            if event.type==pygame.KEYDOWN and player.rect.y+player.rect.width>0:
                if event.key==pygame.K_SPACE:
                    player.jump(FPS)
        player.move_player(FPS)
        delay+=1
        if delay>=FPS*1.5:
            pipe=Pipes(1100,random.randrange(150, 450), *GREEN_PIPE.get_size() , GREEN_PIPE)
            flipped_pipe=Pipes(1100, pipe.rect.y-FLIPPED_GREEN_PIPE.get_height()-120,*FLIPPED_GREEN_PIPE.get_size(), FLIPPED_GREEN_PIPE , True)
            pipes.extend( [pipe, flipped_pipe])
            delay=0
        for pipe in pipes[:]:
            pipe.move(PIPE_SPEED)
            if pipe.rect.x+pipe.rect.width+4<=0:
                pipes.remove(pipe)
            if pipe.rect.x+pipe.rect.width<player.rect.x+player.rect.width and pipe.passed==False and pipe.flipped==False:
                score+=1
                pipe.passed=True
        draw_window(base, player, pipes, score)
        if collision_base(player, base):
            WIN.blit(GAME_OVER_TEXT, (WIDTH/2 -GAME_OVER_TEXT.get_width()/2,HEIGHT/2- GAME_OVER_TEXT.get_height()/2))
            pygame.display.update()
            pygame.time.delay(4000)
            break
        if collision_pipes(player, pipes):
            WIN.blit(GAME_OVER_TEXT, (WIDTH/2 -GAME_OVER_TEXT.get_width()/2,HEIGHT/2- GAME_OVER_TEXT.get_height()/2))
            pygame.display.update()
            pygame.time.delay(4000)
            break
    pygame.quit()
if __name__=="__main__":
    main()






            
