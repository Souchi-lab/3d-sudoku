
import unittest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.database import Base, Rank, db_session, init_db
from api.database import Base, Rank, db_session, init_db

def add_rank(player_name, score, level, session):
    new_rank = Rank(player_name=player_name, score=score, level=level)
    session.add(new_rank)
    session.commit()

def get_ranks(level=None, session=None):
    sess = session if session else db_session
    if level:
        ranks = sess.query(Rank).filter_by(level=level).order_by(Rank.score.desc()).limit(10).all()
    else:
        ranks = sess.query(Rank).order_by(Rank.score.desc()).limit(10).all()
    return [
        {
            'id': rank.id,
            'player_name': rank.player_name,
            'score': rank.score,
            'level': rank.level,
            'timestamp': rank.timestamp.isoformat()
        } for rank in ranks
    ]

class TestDatabaseIntegration(unittest.TestCase):

    def setUp(self):
        # Use an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Patch db_session to use our in-memory database
        self.db_session_patcher = patch('api.app.db_session', self.session)
        self.db_session_patcher.start()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.db_session_patcher.stop()

    def test_add_and_get_ranks(self):
        # 2.4: DB ランキング連携 - add_rank & get_ranks 正常系
        # Add a new rank
        player_name = "TestPlayer"
        score = 100
        level = 1
        add_rank(player_name, score, level, self.session)

        # Get ranks and verify the new rank is present
        ranks = get_ranks(session=self.session)
        self.assertEqual(len(ranks), 1)
        self.assertEqual(ranks[0]['player_name'], player_name)
        self.assertEqual(ranks[0]['score'], score)
        self.assertEqual(ranks[0]['level'], level)

    def test_get_ranks_empty(self):
        # 2.4: DB ランキング連携 - get_ranks (empty)
        # Get ranks when the database is empty
        ranks = get_ranks(session=self.session)
        self.assertEqual(len(ranks), 0)

    def test_add_rank_exception(self):
        # 2.4: DB ランキング連携 - add_rank 例外系
        # Simulate a database error by mocking commit to raise an exception
        with patch.object(self.session, 'commit', side_effect=Exception("DB Error")):
            with self.assertRaises(Exception):
                add_rank("ErrorPlayer", 200, 2, self.session)

if __name__ == '__main__':
    unittest.main()
