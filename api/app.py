from flask import Flask, request, jsonify
from api.database import db_session, init_db, Rank

app = Flask(__name__)

@app.route('/api/rank', methods=['GET', 'POST'])
def rank():
    if request.method == 'POST':
        data = request.get_json()
        player_name = data.get('player_name')
        score = data.get('score')
        level = data.get('level')

        if not all([player_name, score, level]):
            return jsonify({'error': 'Missing data'}), 400

        new_rank = Rank(player_name=player_name, score=score, level=level)
        db_session.add(new_rank)
        db_session.commit()
        return jsonify({'message': 'Rank added successfully'}), 201

    elif request.method == 'GET':
        level = request.args.get('level')
        if level:
            ranks = Rank.query.filter_by(level=level).order_by(Rank.score.desc()).limit(10).all()
        else:
            ranks = Rank.query.order_by(Rank.score.desc()).limit(10).all()
        
        return jsonify([
            {
                'id': rank.id,
                'player_name': rank.player_name,
                'score': rank.score,
                'level': rank.level,
                'timestamp': rank.timestamp.isoformat()
            } for rank in ranks
        ])

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
