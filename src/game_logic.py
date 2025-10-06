import random
import curses
import time
from datetime import datetime

class SnakeGame:
    def __init__(self, width=20, height=20, session_id=None, max_obstacles=10):
        self.width = width
        self.height = height
        self.session_id = session_id or self._generate_session_id()
        self.max_obstacles = max_obstacles
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
        self.paused = False
        self.speed = 600  # 初始速度(ms)
        self.moves_count = 0
        self.obstacles = self.generate_obstacles()
        self.high_score = 0
    
    def generate_food(self):
        while True:
            food = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if food not in self.snake and food not in self.obstacles:
                return food

    def generate_obstacles(self):
        obstacles = set()
        while len(obstacles) < self.max_obstacles:
            pos = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if pos != (self.width // 2, self.height // 2):
                obstacles.add(pos)
        return list(obstacles)
    
    def change_direction(self, new_direction):
        opposite = {'UP':'DOWN','DOWN':'UP','LEFT':'RIGHT','RIGHT':'LEFT'}
        if new_direction != opposite.get(self.direction):
            self.direction = new_direction
    
    def move(self):
        if self.game_over or self.paused:
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
        
        # 碰撞检测
        if (new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height or
            new_head in self.snake or
            new_head in self.obstacles):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
            return False
        
        self.snake.insert(0, new_head)
        self.moves_count += 1
        
        # 吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            
            # 升级加速
            if self.score % 50 == 0:
                self.level += 1
                if self.speed > 100:
                    self.speed -= 20
            return True
        else:
            self.snake.pop()
            return False

    def get_state(self):
        return {
            'id': self.session_id,
            'snake': self.snake,
            'food': self.food,
            'score': self.score,
            'level': self.level,
            'direction': self.direction,
            'game_over': self.game_over,
            'speed': self.speed,
            'width': self.width,
            'height': self.height,
            'moves_count': self.moves_count,
            'obstacles': self.obstacles,
            'high_score': self.high_score
        }

    def from_dict(self, data):
        self.session_id = data['id']
        self.snake = data['snake']
        self.food = data['food']
        self.score = data['score']
        self.level = data.get('level', 1)
        self.direction = data['direction']
        self.game_over = data['game_over']
        self.speed = data.get('speed', 600)
        self.width = data['width']
        self.height = data['height']
        self.moves_count = data.get('moves_count', 0)
        self.obstacles = data.get('obstacles', [])
        self.high_score = data.get('high_score', 0)

    def render(self, stdscr):
        stdscr.clear()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 蛇
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # 食物
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # 边框
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # 文字
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # 障碍
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK) # 蛇头
        
        # 边框
        for x in range(self.width + 2):
            stdscr.addstr(0, x * 2, "██", curses.color_pair(3))
            stdscr.addstr(self.height + 1, x * 2, "██", curses.color_pair(3))
        for y in range(1, self.height + 1):
            stdscr.addstr(y, 0, "██", curses.color_pair(3))
            stdscr.addstr(y, (self.width + 1) * 2, "██", curses.color_pair(3))
        
        # 蛇
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                stdscr.addstr(y + 1, (x + 1) * 2, "██", curses.color_pair(6))
            else:
                stdscr.addstr(y + 1, (x + 1) * 2, "██", curses.color_pair(1))
        
        # 食物
        fx, fy = self.food
        stdscr.addstr(fy + 1, (fx + 1) * 2, "██", curses.color_pair(2))
        
        # 障碍
        for ox, oy in self.obstacles:
            stdscr.addstr(oy + 1, (ox + 1) * 2, "██", curses.color_pair(5))
        
        # 信息
        stdscr.addstr(self.height + 3, 0, f"Score: {self.score}  High: {self.high_score}  Level: {self.level}  Speed: {self.speed}ms", curses.color_pair(4))
        if self.paused:
            stdscr.addstr(self.height + 4, 0, "PAUSED - Press 'p' to continue", curses.color_pair(4))
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

        while True:
            try:
                next_key = stdscr.getch()
                if next_key != -1:
                    key = next_key
                    if key in key_map:
                        self.change_direction(key_map[key])
                    elif key in [ord('p'), ord('P')]:
                        self.paused = not self.paused
                    elif key in [ord('q'), ord('Q')]:
                        break
                    elif key in [ord('r'), ord('R')] and self.game_over:
                        self.reset()
                
                self.move()
                self.render(stdscr)
                time.sleep(self.speed / 1000.0)
            except KeyboardInterrupt:
                break

        stdscr.addstr(self.height + 5, 0, "Game exited. Press any key.", curses.color_pair(4))
        stdscr.nodelay(False)
        stdscr.getch()

# 运行游戏
if __name__ == "__main__":
    game = SnakeGame(width=25, height=20, max_obstacles=15)
    game.run()
