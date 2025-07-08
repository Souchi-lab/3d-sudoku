import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from api.app import app as flask_app
from api.database import Base, Rank, init_db, db_session, engine # Import original db_session and engine for patching

class TestAPI(unittest.TestCase):

    def setUp(self):
        # Create a new Flask app instance for each test
        self.app = flask_app.test_client()
        self.app_context = flask_app.app_context()
        self.app_context.push()

        # Configure the app to use an in-memory SQLite database
        flask_app.config['TESTING'] = True
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        # Create a new in-memory engine for this test
        self.test_engine = create_engine('sqlite:///:memory:')

        # Patch the global engine in api.database
        self.engine_patch = patch('api.database.engine', self.test_engine)
        self.engine_patch.start()

        # Create a new scoped_session that uses the test_engine
        # and patch the global db_session in api.database to this new session
        self.TestSessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=self.test_engine)
        self.test_db_session = scoped_session(self.TestSessionMaker)

        # Create a mock for scoped_session that delegates to our test_db_session
        mock_db_session_for_app = MagicMock(wraps=self.test_db_session)
        mock_db_session_for_app.remove = MagicMock() # Ensure it has a remove method

        # Patch the db_session used by the Flask app to point to our mock
        self.db_session_patch = patch('api.app.db_session', mock_db_session_for_app)
        self.db_session_patch.start()

        # Create tables in the in-memory database
        with flask_app.app_context():
            Base.metadata.drop_all(bind=self.test_engine) # Ensure a clean slate
            init_db()

    def tearDown(self):
        self.test_db_session.close() # Close the session
        Base.metadata.drop_all(bind=self.test_engine) # Drop all tables
        self.test_engine.dispose() # Dispose the engine
        self.app_context.pop() # Pop the app context

        # Stop all patches
        self.db_session_patch.stop()
        self.engine_patch.stop() # Add this line

    @unittest.skip("ランキング機能を含むためスキップします。")
    @unittest.skip("ランキング機能を含むためスキップします。")
    def test_post_rank_success(self):
        response = self.app.post(
            '/api/rank',
            json={'player_name': 'TestPlayer', 'score': 100, 'level': 1}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'message': 'Rank added successfully'})

        # Verify directly from the test_db_session
        rank = self.test_db_session.query(Rank).first()
        self.assertIsNotNone(rank)
        self.assertEqual(rank.player_name, 'TestPlayer')
        self.assertEqual(rank.score, 100)
        self.assertEqual(rank.level, 1)

    @unittest.skip("ランキング機能を含むためスキップします。")
    def test_post_rank_missing_data(self):
        response = self.app.post(
            '/api/rank',
            json={'player_name': 'TestPlayer', 'score': 100}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Missing data'})
    
    @unittest.skip("ランキング機能を含むためスキップします。")
    def test_get_ranks_all(self):
        self.test_db_session.add(Rank(player_name='PlayerA', score=100, level=1))
        self.test_db_session.add(Rank(player_name='PlayerB', score=200, level=2))
        self.test_db_session.add(Rank(player_name='PlayerC', score=150, level=1))
        self.test_db_session.commit()

        response = self.app.get('/api/rank')
        self.assertEqual(response.status_code, 200)
        ranks = response.json
        self.assertEqual(len(ranks), 3)
        self.assertEqual(ranks[0]['player_name'], 'PlayerB') # Ordered by score desc
        self.assertEqual(ranks[1]['player_name'], 'PlayerC')
        self.assertEqual(ranks[2]['player_name'], 'PlayerA')

    @unittest.skip("ランキング機能を含むためスキップします。")
    def test_get_ranks_by_level(self):
        self.test_db_session.add(Rank(player_name='PlayerA', score=100, level=1))
        self.test_db_session.add(Rank(player_name='PlayerB', score=200, level=2))
        self.test_db_session.add(Rank(player_name='PlayerC', score=150, level=1))
        self.test_db_session.commit()

        response = self.app.get('/api/rank?level=1')
        self.assertEqual(response.status_code, 200)
        ranks = response.json
        self.assertEqual(len(ranks), 2)
        self.assertEqual(ranks[0]['player_name'], 'PlayerC') # Ordered by score desc
        self.assertEqual(ranks[1]['player_name'], 'PlayerA')

    @unittest.skip("ランキング機能を含むためスキップします。")
    def test_get_ranks_empty(self):
        response = self.app.get('/api/rank')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

if __name__ == '__main__':
    unittest.main()