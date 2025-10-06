import random
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
        self.score = 0
        self.level = 1
        self.game_over = False
        self.speed = 600
        self.moves_count = 0
        self.food = self._generate_food()

    def _generate_food(self):
        """生成一个不在蛇身上的食物"""
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.snake:
                return (x, y)
    
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
        else:  # RIGHT
            new_head = (head_x + 1, head_y)
        
        # 撞墙或撞自己
        if (new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height or
            new_head in self.snake):
            self.game_over = True
            return False
        
        self.snake.insert(0, new_head)
        self.moves_count += 1

        # 吃食物
        if new_head == self.food:
            self.score += 10
            self.food = self._generate_food()  # 生成新食物
            if self.score % 50 == 0 and self.speed > 50:
                self.level += 1
                self.speed -= 10
        else:
            self.snake.pop()
        
        return True
    
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
            'moves_count': self.moves_count
        }

    def render(self):
        board = ""
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) == self.snake[0]:
                    board += "🟢"  # 蛇头
                elif (x, y) in self.snake[1:]:
                    board += "🟩"  # 蛇身
                elif (x, y) == self.food:
                    board += "🍎"  # 食物
                else:
                    board += "⬛"  # 空白
            board += "\n"
        board += f"Score: {self.score}  Level: {self.level}  Speed: {self.speed}ms\n"
        if self.game_over:
            board += "💀 Game Over 💀\n"
        return board
