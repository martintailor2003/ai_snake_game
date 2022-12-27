import pygame
import random
from enum import Enum
from collections import namedtuple
from settings import *
pygame.init()
font = pygame.font.SysFont('arial', 20)
Point = namedtuple('Point', 'x, y')

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

#MAIN class
class SnakeGame:
    def __init__(self, w=640, h=480):
        print('Init')
        self.w = w
        self.h = h
        self.game_number = 0
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('SnakeGame By AI')
        self.clock = pygame.time.Clock()
        self.new_game()
        
    def new_game(self):
        print("new game")
        r = random.randint(0,3)
        if r == 0: 
            self.direction = Direction.UP
        elif r == 1: 
            self.direction = Direction.RIGHT
        elif r == 2:
            self.direction = Direction.DOWN
        elif r == 3: 
            self.direction = Direction.LEFT
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self.move_count = 0
        self._place_food()


    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self,task, max_score):
        self.max_score = max_score
        self.move_count += 1
        increment_decrement = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        #move
        self._move(task) # update the head
        self.snake.insert(0, self.head)
        
        #check game status
        game_over = False
        if self.is_collision() or self.move_count >  100*len(self.snake):
            self.move_count = 0
            game_over = True
            increment_decrement = -10
            self.game_number += 1
            return game_over, self.score, increment_decrement
            
        #drop food
        if self.head == self.food:
            self.score += 1
            increment_decrement = 10
            self.move_count = 0
            self._place_food()
        else:
            self.snake.pop()

        #update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        return game_over, self.score, increment_decrement
    
    def is_collision(self, pt = None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)
        for pt in self.snake:
            pygame.draw.rect(self.display, GREEN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, RED, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text0 = font.render("Current score: " + str(self.score), True, GREEN)
        text1 = font.render("Peek score:" + str(self.max_score), True, GREEN)
        text2 = font.render("Game Number:" + str(self.game_number), True, GREEN)

        self.display.blit(text0, [10, 0])
        self.display.blit(text1, [200,0])
        self.display.blit(text2, [400,0])

        pygame.display.flip()
        
    def _move(self, d):
        
        x = self.head.x
        y = self.head.y
        direction1 = Direction.RIGHT
        if self.direction == Direction.RIGHT:
            if d == 1:
                direction1 = Direction.DOWN
            elif d == 2:
                direction1 = Direction.UP
            else:
                direction1 = self.direction
        elif self.direction == Direction.UP:
            if d == 1:
                direction1 = Direction.RIGHT
            elif d == 2:
                direction1 = Direction.LEFT
            else:
                direction1 = self.direction
        elif self.direction == Direction.LEFT:
            if d == 1:
                direction1 = Direction.UP
            elif d == 2:
                direction1 = Direction.DOWN
            else:
                direction1 = self.direction
        elif self.direction == Direction.DOWN:
            if d == 1:
                self.direction1 = Direction.LEFT
            elif d == 2:
                direction1 = Direction.RIGHT
            else:
                direction1 = self.direction
        
        self.direction = direction1        
        
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)


