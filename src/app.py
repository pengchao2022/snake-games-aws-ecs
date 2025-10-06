from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from models import db
from database import init_db, save_game_session, get_game_session, save_high_score, get_high_scores
from game_logic import SnakeGame
from sqlalchemy import text
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 初始化数据库
init_db(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game/start', methods=['POST'])
def start_game():
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        player_name = data.get('player_name')
        width = data.get('width', 20)
        height = data.get('height', 20)

        game = SnakeGame(width=width, height=height, session_id=session_id)

        # 保存初始状态到数据库
        game_state = game.get_state()
        if player_name:
            game_state['player_name'] = player_name

        saved_state = save_game_session(game_state)

        return jsonify({
            'success': True,
            'game_state': saved_state
        })
    except Exception as e:
        logger.error(f"Error starting game: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/game/move', methods=['POST'])
def make_move():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        direction = data.get('direction')

        if not session_id or not direction:
            return jsonify({'success': False, 'error': 'Missing session_id or direction'}), 400

        saved_state = get_game_session(session_id)
        if not saved_state:
            return jsonify({'success': False, 'error': 'Game session not found'}), 404

        game = SnakeGame()
        game.from_dict(saved_state)
        game.change_direction(direction)
        food_eaten = game.move()

        updated_state = game.get_state()
        save_game_session(updated_state)

        return jsonify({'success': True, 'game_state': updated_state, 'food_eaten': food_eaten})
    except Exception as e:
        logger.error(f"Error making move: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'Missing session_id'}), 400

        saved_state = get_game_session(session_id)
        if not saved_state:
            return jsonify({'success': False, 'error': 'Game session not found'}), 404

        return jsonify({'success': True, 'game_state': saved_state})
    except Exception as e:
        logger.error(f"Error getting game state: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'Missing session_id'}), 400

        saved_state = get_game_session(session_id)
        if not saved_state:
            return jsonify({'success': False, 'error': 'Game session not found'}), 404

        game = SnakeGame(
            width=saved_state['width'],
            height=saved_state['height'],
            session_id=session_id
        )
        updated_state = game.get_state()
        if saved_state.get('player_name'):
            updated_state['player_name'] = saved_state['player_name']

        save_game_session(updated_state)

        return jsonify({'success': True, 'game_state': updated_state})
    except Exception as e:
        logger.error(f"Error resetting game: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scores/high-scores', methods=['GET'])
def get_high_scores_list():
    try:
        limit = request.args.get('limit', 10, type=int)
        scores = get_high_scores(limit)
        return jsonify({'success': True, 'high_scores': scores})
    except Exception as e:
        logger.error(f"Error getting high scores: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scores/save', methods=['POST'])
def save_score():
    try:
        data = request.get_json()
        player_name = data.get('player_name')
        score = data.get('score')
        level = data.get('level', 1)
        duration = data.get('duration', 0)

        if not player_name or score is None:
            return jsonify({'success': False, 'error': 'Missing player_name or score'}), 400

        saved_score = save_high_score(player_name, score, level, duration)
        return jsonify({'success': True, 'high_score': saved_score})
    except Exception as e:
        logger.error(f"Error saving score: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    try:
        # SQLAlchemy 3.x 兼容写法
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'environment': os.environ.get('ENVIRONMENT', 'unknown')
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug)
