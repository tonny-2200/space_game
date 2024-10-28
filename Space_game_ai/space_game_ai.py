import neat.nn.feed_forward
import pygame
import random
import neat
import time
import os 
pygame.font.init()
WIN_WIDTH = 800
WIN_HEIGHT = 800
# BIRD_IMAGES NOT BIRD_IMGS
ROCKET_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("C:\\Users\\tanma\\OneDrive\\Desktop\\Space_game_ai\\imgs","rocket3.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("C:\\Users\\tanma\\OneDrive\\Desktop\\Space_game_ai\\imgs","rocket3.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("C:\\Users\\tanma\\OneDrive\\Desktop\\Space_game_ai\\imgs","rocket3.png")))]

PIPE_IMAGES = pygame.transform.scale2x(pygame.image.load(os.path.join("C:\\Users\\tanma\\OneDrive\\Desktop\\Space_game_ai\\imgs","space_pipe.png")))

BASE_IMAGES = pygame.transform.scale2x(pygame.image.load(os.path.join("C:\\Users\\tanma\\OneDrive\\Desktop\\Space_game_ai\\imgs","space_base.png")))
BG_IMAGES = pygame.transform.scale2x(pygame.image.load(os.path.join("C:\\Users\\tanma\\OneDrive\\Desktop\\Space_game_ai\\imgs","space_bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Rocket:
    IMGS = ROCKET_IMAGES         # Constants
    MAX_ROTATION = 5
    ROT_VEL = 30
    ANIMATION_TIME = 10

    def __init__(self,x,y):     # Constructor 
        self.x = x              # Default position of bird
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        
    def jump(self):             # Method
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
    
    def move(self):
        self.tick_count += 1
        
        ds = self.vel*self.tick_count + 1.5*self.tick_count**2 # ut+ half at**2 (kinematic equation)
        if ds >= 16:
            ds = 16
        if ds < 0:
            ds -= 2
            
        self.y = self.y + ds
        if ds < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self,win): #8.19 vid 2
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
            
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
        
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center)
        win.blit(rotated_image,new_rect.topleft)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
           

class Pipe:
    GAP = 200
    VEL = 5
    
    
    
    
    def __init__(self,x):
        self.x = x
        self.height = 0
        self.gap = 100
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGES, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGES
        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
    
    def move(self):
        self.x -= self.VEL
        
    
    def draw(self, win):
        win.blit(self.PIPE_TOP,(self.x , self.top))
        win.blit(self.PIPE_BOTTOM,(self.x , self.bottom))
        
    def collide(self,rocket):
        rocket_mask = rocket.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        top_offset = (self.x - rocket.x, self.top - round(rocket.y))
        bottom_offset = (self.x - rocket.x, self.bottom - round(rocket.y))
        
        b_point = rocket_mask.overlap(bottom_mask, bottom_offset)
        t_point = rocket_mask.overlap(top_mask, top_offset)
        
        if t_point or b_point:
            return True
        return False
    
class Base:
    VEL = 5
    WIDTH = BASE_IMAGES.get_width()
    IMG = BASE_IMAGES
    
    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH 
        
    def draw(self, win):
        win.blit(self.IMG,(self.x1 , self.y))
        win.blit(self.IMG,(self.x2 , self.y))
        
        
def draw_window(win, rockets,pipes,base, score):
    win.blit(BG_IMAGES,(0,0))
    for pipe in pipes:
        pipe.draw(win)
        
    text = STAT_FONT.render('Score: '+ str(score),1,(255,255,255))
    win.blit(text,(WIN_WIDTH - 10 - text.get_width(),10))
    base.draw(win)
    for rocket in rockets:
        rocket.draw(win)
    pygame.display.update()
    


def main(genomes, config):
    nets = []
    ge = []
    rockets = []
    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        rockets.append(Rocket(230,350))
        g.fitness = 0
        ge.append(g)
    
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    base = Base(700)
    pipes = [Pipe(650)]
    clock = pygame.time.Clock()
    score = 0
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        pipe_ind = 0
        if len(rockets) > 0:
            if len(pipes) > 1 and rockets[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break
            
        for x, rocket in enumerate(rockets):
            rocket.move()
            ge[x].fitness += 0.1
            
            output = nets[x].activate((rocket.y, abs(rocket.y - pipes[pipe_ind].height), abs(rocket.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                rocket.jump()
            
               
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x,rocket in enumerate(rockets):
                if pipe.collide(rocket):
                    ge[x].fitness -= 1
                    rockets.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    
            
                if not pipe.passed and pipe.x < rocket.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
                
            pipe.move()
            
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))
            
        for r in rem:
            pipes.remove(r)
        for x, rocket in enumerate(rockets):
            if rocket.y + rocket.img.get_height() >= 730 or rocket.y < 0:
                rockets.pop(x)
                nets.pop(x)
                ge.pop(x)
                
        base.move()
        draw_window(win,rockets,pipes,base,score)
    
  
     

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main,50)
    
       
       
       
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-Ai.txt")
    run(config_path)