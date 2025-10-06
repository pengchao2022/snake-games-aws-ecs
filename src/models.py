from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.String(64), primary_key=True)
    player_name = db.Column(db.String(100), nullable=True)
    score = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    snake_data = db.Column(db.Text, nullable=False)  # JSON string of snake positions
    food_position = db.Column(db.Text, nullable=False)  # JSON string of food position
    direction = db.Column(db.String(10), default='RIGHT')
    game_over = db.Column(db.Boolean, default=False)
    width = db.Column(db.Integer, default=20)
    height = db.Column(db.Integer, default=20)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'player_name': self.player_name,
            'score': self.score,
            'level': self.level,
            'snake': json.loads(self.snake_data),
            'food': json.loads(self.food_position),
            'direction': self.direction,
            'game_over': self.game_over,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class HighScore(db.Model):
    __tablename__ = 'high_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, default=1)
    game_duration = db.Column(db.Integer, default=0)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'player_name': self.player_name,
            'score': self.score,
            'level': self.level,
            'game_duration': self.game_duration,
            'created_at': self.created_at.isoformat()
        }