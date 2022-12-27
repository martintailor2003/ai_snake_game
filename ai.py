import torch
import random
import numpy as np
from collections import deque
from ai_snake_game import SnakeGame, Direction, Point
from model import Linear_QNet, QTrainer
from settings import *


class Train:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MEMORY)
        self.model = Linear_QNet(11, HIDDEN_L, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.max_score = 0

    def get_data(self,game):
        #position
        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        # direcrion
        up = False
        right = False
        down = False
        left = False
        if game.direction == Direction.UP:
            up = True
        if game.direction == Direction.RIGHT:
            right = True
        if game.direction == Direction.DOWN:
            down = True
        if game.direction == Direction.LEFT:
            left = True

        #create data list
        data = [
            #border straight
            (up and game.is_collision(point_u)) or
            (right and game.is_collision(point_r)) or
            (down and game.is_collision(point_d)) or
            (left and game.is_collision(point_l))
            ,
            #border right
            (up and game.is_collision(point_r)) or
            (right and game.is_collision(point_d)) or
            (down and game.is_collision(point_l)) or
            (left and game.is_collision(point_u))
            ,
            #border left
            (up and game.is_collision(point_l)) or
            (right and game.is_collision(point_u)) or
            (down and game.is_collision(point_r)) or
            (left and game.is_collision(point_d)),
            #Boolean directions
            up,
            right,
            down,
            left,
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]
        return np.array(data, dtype=int)
    
    def get_ai_move(self, state):
        self.epsilon = 80 - self.n_games
        move = 0
        output_list = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            print("Predetention:",prediction)
            move = torch.argmax(prediction).item()
        output_list[move] = 1
        return move, output_list

    def train_short(self, state_data, output_list, increment_decrement, new_stat_data, game_over):
        self.trainer.train_step(state_data, output_list, increment_decrement, new_stat_data, game_over)
    
    def remember(self,state_data, output_list, increment_decrement, new_stat_data, game_over):    
        self.memory.append((state_data, output_list, increment_decrement, new_stat_data, game_over))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
    
   



def main():
    game = SnakeGame()
    train = Train()
    while True:
        # get old state
        state_old = train.get_data(game)

        # get move
        move, output_list  = train.get_ai_move(state_old)

        # perform move and get new state
        done, score, reward= game.play_step(move, train.max_score)
        
        state_new = train.get_data(game)

        # train short memory
        print(state_old, output_list, reward, state_new, done)
        train.train_short(state_old, output_list, reward, state_new, done)

        # remember
        train.remember(state_old, output_list, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.new_game()
            train.n_games += 1
            train.train_long_memory()

            if score > train.max_score:
                train.max_score = score
                train.model.save()


    

if __name__ == '__main__':
    main()