class SnakeGameUI {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 20;
        this.gameState = null;
        this.sessionId = null;
        this.gameLoop = null;
        this.lastMoveTime = 0;
        this.isPaused = false;
        
        this.initializeGame();
        this.setupEventListeners();
        this.loadHighScores();
    }
    
    initializeGame() {
        // 设置画布大小
        this.canvas.width = 20 * this.gridSize;
        this.canvas.height = 20 * this.gridSize;
        
        // 生成会话ID
        this.sessionId = 'session_' + Date.now();
        
        // 显示玩家姓名表单
        this.showPlayerForm();
    }
    
    showPlayerForm() {
        const gameInfo = document.querySelector('.game-info');
        gameInfo.innerHTML = `
            <div class="player-form">
                <h3>开始新游戏</h3>
                <div class="form-group">
                    <label for="playerName">请输入您的姓名:</label>
                    <input type="text" id="playerName" placeholder="匿名玩家" maxlength="20" value="匿名玩家">
                </div>
                <button class="btn btn-primary" onclick="gameUI.startGame()">开始游戏</button>
            </div>
            <div class="high-scores">
                <h3>高分榜</h3>
                <ul id="highScoresList"></ul>
            </div>
        `;
    }
    
    async startGame() {
        const playerName = document.getElementById('playerName').value || '匿名玩家';
        
        try {
            const response = await fetch('/api/game/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    player_name: playerName,
                    width: 20,
                    height: 20
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.gameState = data.game_state;
                this.renderGameInfo();
                this.startGameLoop();
            } else {
                alert('游戏启动失败: ' + data.error);
            }
        } catch (error) {
            console.error('Error starting game:', error);
            alert('游戏启动失败，请检查网络连接');
        }
    }
    
    renderGameInfo() {
        const gameInfo = document.querySelector('.game-info');
        gameInfo.innerHTML = `
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-label">玩家:</span>
                    <span class="stat-value">${this.gameState.player_name || '匿名玩家'}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">分数:</span>
                    <span class="stat-value" id="score">${this.gameState.score}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">等级:</span>
                    <span class="stat-value" id="level">${this.gameState.level}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">长度:</span>
                    <span class="stat-value" id="length">${this.gameState.snake.length}</span>
                </div>
            </div>
            
            <div class="controls">
                <div class="control-buttons">
                    <button class="btn btn-success" onclick="gameUI.changeDirection('UP')">↑ 上</button>
                    <button class="btn btn-success" onclick="gameUI.changeDirection('DOWN')">↓ 下</button>
                    <button class="btn btn-success" onclick="gameUI.changeDirection('LEFT')">← 左</button>
                    <button class="btn btn-success" onclick="gameUI.changeDirection('RIGHT')">→ 右</button>
                </div>
                <div class="control-buttons">
                    <button class="btn btn-primary" onclick="gameUI.resetGame()">重新开始</button>
                    <button class="btn btn-danger" onclick="gameUI.pauseGame()">${this.isPaused ? '继续' : '暂停'}</button>
                </div>
                <div class="control-keys">
                    <p>使用方向键或WASD控制蛇的移动</p>
                    <p>空格键: 暂停/继续</p>
                </div>
            </div>
            
            <div id="gameOverMessage" style="display: none;" class="game-over">
                <h3>游戏结束!</h3>
                <p>最终分数: <span id="finalScore">0</span></p>
                <button class="btn btn-primary" onclick="gameUI.resetGame()">再玩一次</button>
            </div>
            
            <div class="high-scores">
                <h3>高分榜</h3>
                <ul id="highScoresList"></ul>
            </div>
        `;
        
        this.loadHighScores();
    }
    
    async changeDirection(direction) {
        if (!this.gameState || this.gameState.game_over || this.isPaused) return;
        
        try {
            const response = await fetch('/api/game/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    direction: direction
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.gameState = data.game_state;
                this.updateDisplay();
                
                if (this.gameState.game_over) {
                    this.handleGameOver();
                }
            }
        } catch (error) {
            console.error('Error making move:', error);
        }
    }
    
    startGameLoop() {
        this.lastMoveTime = 0;
        this.isPaused = false;
        
        const gameLoop = (timestamp) => {
            if (!this.gameState || this.gameState.game_over || this.isPaused) {
                this.gameLoop = requestAnimationFrame(gameLoop);
                return;
            }
            
            if (!this.lastMoveTime) {
                this.lastMoveTime = timestamp;
            }
            
            const elapsed = timestamp - this.lastMoveTime;
            
            if (elapsed > this.gameState.speed) {
                // 自动移动（继续当前方向）
                this.changeDirection(this.gameState.direction);
                this.lastMoveTime = timestamp;
            }
            
            this.gameLoop = requestAnimationFrame(gameLoop);
        };
        
        this.gameLoop = requestAnimationFrame(gameLoop);
    }
    
    stopGameLoop() {
        if (this.gameLoop) {
            cancelAnimationFrame(this.gameLoop);
            this.gameLoop = null;
        }
    }
    
    async resetGame() {
        this.stopGameLoop();
        this.isPaused = false;
        
        try {
            const response = await fetch('/api/game/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.gameState = data.game_state;
                this.updateDisplay();
                this.startGameLoop();
                
                // 隐藏游戏结束消息
                const gameOverMsg = document.getElementById('gameOverMessage');
                if (gameOverMsg) {
                    gameOverMsg.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Error resetting game:', error);
        }
    }
    
    pauseGame() {
        this.isPaused = !this.isPaused;
        this.updatePauseButton();
    }
    
    updatePauseButton() {
        const pauseButton = document.querySelector('.btn-danger');
        if (pauseButton) {
            pauseButton.textContent = this.isPaused ? '继续' : '暂停';
        }
    }
    
    handleGameOver() {
        this.stopGameLoop();
        
        // 显示游戏结束消息
        const gameOverMsg = document.getElementById('gameOverMessage');
        const finalScore = document.getElementById('finalScore');
        
        if (gameOverMsg && finalScore) {
            finalScore.textContent = this.gameState.score;
            gameOverMsg.style.display = 'block';
        }
        
        // 保存分数
        this.saveScore();
    }
    
    async saveScore() {
        try {
            await fetch('/api/scores/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    player_name: this.gameState.player_name || '匿名玩家',
                    score: this.gameState.score,
                    level: this.gameState.level,
                    duration: Math.floor(this.gameState.moves_count * this.gameState.speed / 1000)
                })
            });
            
            // 刷新高分榜
            this.loadHighScores();
        } catch (error) {
            console.error('Error saving score:', error);
        }
    }
    
    async loadHighScores() {
        try {
            const response = await fetch('/api/scores/high-scores?limit=10');
            const data = await response.json();
            
            if (data.success) {
                this.renderHighScores(data.high_scores);
            }
        } catch (error) {
            console.error('Error loading high scores:', error);
        }
    }
    
    renderHighScores(scores) {
        const scoresList = document.getElementById('highScoresList');
        if (!scoresList) return;
        
        if (scores.length === 0) {
            scoresList.innerHTML = '<li>暂无记录</li>';
            return;
        }
        
        scoresList.innerHTML = scores.map(score => `
            <li>
                <span>${score.player_name}</span>
                <span>${score.score}分</span>
            </li>
        `).join('');
    }
    
    updateDisplay() {
        this.drawGame();
        
        // 更新分数和等级显示
        const scoreElement = document.getElementById('score');
        const levelElement = document.getElementById('level');
        const lengthElement = document.getElementById('length');
        
        if (scoreElement) scoreElement.textContent = this.gameState.score;
        if (levelElement) levelElement.textContent = this.gameState.level;
        if (lengthElement) lengthElement.textContent = this.gameState.snake.length;
    }
    
    drawGame() {
        // 清空画布
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        if (!this.gameState) return;
        
        // 绘制网格
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 0.5;
        for (let x = 0; x <= this.canvas.width; x += this.gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = 0; y <= this.canvas.height; y += this.gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
        
        // 绘制蛇
        this.gameState.snake.forEach((segment, index) => {
            if (index === 0) {
                // 蛇头
                this.ctx.fillStyle = '#4CAF50';
            } else {
                // 蛇身
                this.ctx.fillStyle = '#8BC34A';
            }
            
            this.ctx.fillRect(
                segment[0] * this.gridSize,
                segment[1] * this.gridSize,
                this.gridSize - 1,
                this.gridSize - 1
            );
        });
        
        // 绘制食物
        this.ctx.fillStyle = '#FF5252';
        this.ctx.beginPath();
        const foodX = this.gameState.food[0] * this.gridSize + this.gridSize / 2;
        const foodY = this.gameState.food[1] * this.gridSize + this.gridSize / 2;
        const radius = this.gridSize / 2 - 2;
        this.ctx.arc(foodX, foodY, radius, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    setupEventListeners() {
        // 键盘控制
        document.addEventListener('keydown', (e) => {
            if (!this.gameState || this.gameState.game_over) return;
            
            switch(e.key) {
                case 'ArrowUp':
                case 'w':
                case 'W':
                    e.preventDefault();
                    this.changeDirection('UP');
                    break;
                case 'ArrowDown':
                case 's':
                case 'S':
                    e.preventDefault();
                    this.changeDirection('DOWN');
                    break;
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    e.preventDefault();
                    this.changeDirection('LEFT');
                    break;
                case 'ArrowRight':
                case 'd':
                case 'D':
                    e.preventDefault();
                    this.changeDirection('RIGHT');
                    break;
                case ' ':
                    e.preventDefault();
                    this.pauseGame();
                    break;
                case 'r':
                case 'R':
                    e.preventDefault();
                    this.resetGame();
                    break;
            }
        });
    }
}

// 初始化游戏
const gameUI = new SnakeGameUI();