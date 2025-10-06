import random
import curses
import time
from datetime import datetime

class SnakeGame:
    def __init__(self, width=20, height=20, session_id=None):
        self.width = width
        self.height = height
        self.session_id = session_id or self._generate_session_id()
        self.reset()
    
    def _generate_session_id(self):
        return f"session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def reset(self):
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = 'RIGHT'
        self.food = self.generate_food()
        self.score = 0
        self.level = 1
        self.game_over = False
        self.speed = 600  # 初始速度，毫秒
        self.moves_count = 0
    
    def generate_food(self):
        while True:
            food = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if food not in self.snake:
                return food
    
    def change_direction(self, new_direction):
        opposite = {'UP':'DOWN','DOWN':'UP','LEFT':'RIGHT','RIGHT':'LEFT'}
        if new_direction != opposite.get(self.direction):
            self.direction = new_direction
    
    def move(self):
        if self.game_over:
            return False
        
        head_x, head_y = self.snake[0]
        if self.direction == 'UP':
            new_head = (head_x, head_y - 1)
        elif self.direction == 'DOWN':
            new_head = (head_x, head_y + 1)
        elif self.direction == 'LEFT':
            new_head = (head_x - 1, head_y)
        elif self.direction == 'RIGHT':
            new_head = (head_x + 1, head_y)
        
        if (new_head[0] < 0 or new_head[0] >= self.width or 
            new_head[1] < 0 or new_head[1] >= self.height or
            new_head in self.snake):
            self.game_over = True
            return False
        
        self.snake.insert(0, new_head)
        self.moves_count += 1
        
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            if self.score % 50 == 0:
                self.level += 1
                if self.speed > 100:
                    self.speed -= 20
            return True
        else:
            self.snake.pop()
            return False
    
    def render(self, stdscr):
        stdscr.clear()
        board = [['  ' for _ in range(self.width)] for _ in range(self.height)]
        for x, y in self.snake:
            board[y][x] = '🟩'
        food_x, food_y = self.food
        board[food_y][food_x] = '🍎'

        # 打印上边框
        stdscr.addstr('🟥' * (self.width + 2) + '\n')
        for row in board:
            stdscr.addstr('🟥' + ''.join(row) + '🟥\n')
        # 打印下边框
        stdscr.addstr('🟥' * (self.width + 2) + '\n')
        stdscr.addstr(f"Score: {self.score}  Level: {self.level}  Speed: {self.speed}ms\n")
        stdscr.refresh()
    
    def run(self):
        curses.wrapper(self._main_loop)

    def _main_loop(self, stdscr):
        stdscr.nodelay(True)
        key = curses.KEY_RIGHT
        key_map = {
            curses.KEY_UP: 'UP',
            curses.KEY_DOWN: 'DOWN',
            curses.KEY_LEFT: 'LEFT',
            curses.KEY_RIGHT: 'RIGHT',
            ord('w'): 'UP',
            ord('s'): 'DOWN',
            ord('a'): 'LEFT',
            ord('d'): 'RIGHT'
        }

        while not self.game_over:
            try:
                next_key = stdscr.getch()
                if next_key != -1:
                    key = next_key
                if key in key_map:
                    self.change_direction(key_map[key])
                
                self.move()
                self.render(stdscr)
                time.sleep(self.speed / 1000.0)
            except KeyboardInterrupt:
                break
        
        stdscr.addstr("Game Over! Press any key to exit.\n")
        stdscr.nodelay(False)
        stdscr.getch()
