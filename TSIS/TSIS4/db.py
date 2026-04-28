import psycopg2
from psycopg2 import sql
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS


def _connect():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )


SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""

def init_db():
    """Create tables if they don't exist. Returns True on success."""
    try:
        conn = _connect()
        cur  = conn.cursor()
        cur.execute(SCHEMA)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB] init_db error: {e}")
        return False



def get_or_create_player(username: str) -> int | None:
    """Return player id, inserting a new row if needed."""
    try:
        conn = _connect()
        cur  = conn.cursor()
        cur.execute("SELECT id FROM players WHERE username = %s", (username,))
        row = cur.fetchone()
        if row:
            player_id = row[0]
        else:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) RETURNING id",
                (username,)
            )
            player_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return player_id
    except Exception as e:
        print(f"[DB] get_or_create_player error: {e}")
        return None


def get_personal_best(username: str) -> int:
    """Return the player's all-time highest score (0 if none)."""
    try:
        conn = _connect()
        cur  = conn.cursor()
        cur.execute("""
            SELECT COALESCE(MAX(gs.score), 0)
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            WHERE p.username = %s
        """, (username,))
        best = cur.fetchone()[0]
        cur.close()
        conn.close()
        return best
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0



def save_session(player_id: int, score: int, level_reached: int):
    """Persist a completed game session."""
    try:
        conn = _connect()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO game_sessions (player_id, score, level_reached)
            VALUES (%s, %s, %s)
        """, (player_id, score, level_reached))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB] save_session error: {e}")
        return False


def get_leaderboard(limit: int = 10) -> list[dict]:
    """Return top `limit` entries, sorted by score desc."""
    try:
        conn = _connect()
        cur  = conn.cursor()
        cur.execute("""
            SELECT
                p.username,
                gs.score,
                gs.level_reached,
                gs.played_at::date AS played_date
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            ORDER BY gs.score DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {"rank": i+1, "username": r[0], "score": r[1],
             "level": r[2], "date": str(r[3])}
            for i, r in enumerate(rows)
        ]
    except Exception as e:
        print(f"[DB] get_leaderboard error: {e}")
        return []