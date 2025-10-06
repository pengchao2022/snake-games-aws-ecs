import os
import boto3
from flask_sqlalchemy import SQLAlchemy
from models import db, GameSession, HighScore
import json
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """从环境变量或SSM参数存储获取数据库URL"""
    # 首先检查环境变量
    if 'DATABASE_URL' in os.environ:
        return os.environ['DATABASE_URL']
    
    # 如果没有，从SSM参数存储获取
    try:
        environment = os.environ.get('ENVIRONMENT', 'development')
        region = os.environ.get('AWS_REGION', 'us-east-1')
        
        logger.info(f"Getting database URL from SSM for environment: {environment}")
        
        ssm = boto3.client('ssm', region_name=region)
        response = ssm.get_parameter(
            Name=f'/snake-game/{environment}/database-url',
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"Error getting database URL from SSM: {e}")
        # 开发环境回退
        return "postgresql://snakegame:password@localhost:5432/snakegame"

def init_db(app):
    """初始化数据库"""
    database_url = get_database_url()
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    logger.info(f"Initializing database with URL: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

def save_game_session(session_data):
    """保存游戏会话到数据库"""
    try:
        game_session = GameSession.query.get(session_data['id'])
        
        if not game_session:
            game_session = GameSession(
                id=session_data['id'],
                player_name=session_data.get('player_name'),
                width=session_data['width'],
                height=session_data['height']
            )
        
        game_session.score = session_data['score']
        game_session.level = session_data.get('level', 1)
        game_session.snake_data = json.dumps(session_data['snake'])
        game_session.food_position = json.dumps(session_data['food'])
        game_session.direction = session_data['direction']
        game_session.game_over = session_data['game_over']
        
        db.session.add(game_session)
        db.session.commit()
        
        return game_session.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving game session: {e}")
        raise e

def get_game_session(session_id):
    """从数据库获取游戏会话"""
    try:
        game_session = GameSession.query.get(session_id)
        return game_session.to_dict() if game_session else None
    except Exception as e:
        logger.error(f"Error getting game session: {e}")
        return None

def save_high_score(player_name, score, level=1, duration=0):
    """保存高分记录"""
    try:
        high_score = HighScore(
            player_name=player_name,
            score=score,
            level=level,
            game_duration=duration
        )
        
        db.session.add(high_score)
        db.session.commit()
        
        return high_score.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving high score: {e}")
        raise e

def get_high_scores(limit=10):
    """获取高分榜"""
    try:
        high_scores = HighScore.query.order_by(HighScore.score.desc()).limit(limit).all()
        return [score.to_dict() for score in high_scores]
    except Exception as e:
        logger.error(f"Error getting high scores: {e}")
        return []