import asyncpg


DB_PARAMS = {
    'database': 'postgres',
    'user': 'pguser',
    'password': 'pgpassword',
    'host': 'db',
    'port': 5432,
}


async def init() -> None:
    conn: asyncpg.connection = await asyncpg.connect(**DB_PARAMS)
    transaction = conn.transaction()
    await transaction.start()
    await conn.execute('''CREATE TABLE IF NOT EXISTS tg_users
                   (
                    username VARCHAR(400) NOT NULL,
                    client_id VARCHAR(400) NOT NULL,
                    client_secret VARCHAR(400) NOT NULL,
                    UNIQUE(username, client_id, client_secret)
                    );''')
    await transaction.commit()
    await conn.close()


async def add_client_info(username, client_id, client_secret):
    conn: asyncpg.connection = await asyncpg.connect(**DB_PARAMS)
    transaction = conn.transaction()
    await transaction.start()
    await conn.execute('''INSERT INTO tg_users (username, client_id, client_secret)
                       VALUES ($1, $2, $3)''',
                       username, str(client_id), str(client_secret))
    await transaction.commit()
    await conn.close()


async def get_client_info(username):
    conn: asyncpg.connection = await asyncpg.connect(**DB_PARAMS)
    values = await conn.fetch('SELECT * FROM tg_users WHERE username = $1', username)
    await conn.close()
    if values:
        return values[0]
    return None
