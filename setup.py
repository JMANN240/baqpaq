import sqlite3

with sqlite3.connect('database.db') as connection:
    cursor = connection.cursor()

    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('DROP TABLE IF EXISTS visibility')
    cursor.execute('''
        CREATE TABLE visibility (
            visibility_id INTEGER PRIMARY KEY,
            visibility_type TEXT NOT NULL
        )
    ''')

    visibilities = [(1, 'Private'), (2, 'Unlisted'), (3, 'Public')]
    cursor.executemany('INSERT INTO visibility VALUES (?, ?)', visibilities)

    cursor.execute('DROP TABLE IF EXISTS codes')
    cursor.execute('''
        CREATE TABLE codes (
            code_id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            visibility INTEGER NOT NULL,
            CONSTRAINT fk_visibility
                FOREIGN KEY (visibility)
                REFERENCES visibility (visibility),
            CONSTRAINT fk_owner_id
                FOREIGN KEY (owner_id)
                REFERENCES users (user_id)
        )
    ''')

    cursor.execute('DROP TABLE IF EXISTS users_codes')
    cursor.execute('''
        CREATE TABLE users_codes (
            user_id INTEGER NOT NULL,
            code_id INTEGER NOT NULL,
            CONSTRAINT fk_user_id
                FOREIGN KEY (user_id)
                REFERENCES users (user_id),
            CONSTRAINT fk_code_id
                FOREIGN KEY (code_id)
                REFERENCES users (code_id)
        )
    ''')

    cursor.execute('INSERT INTO users (username, password) VALUES ("ted", "ass")')
    cursor.execute('''INSERT INTO codes (title, content, owner_id, visibility) VALUES ("really fucking", "@app.route('/api/codes')
def api_codes():
    with sqlite3.connect('database.db') as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(\'\'\'
            SELECT * FROM codes WHERE code_id IN (
                SELECT code_id FROM users_codes WHERE user_id = (
                    SELECT user_id FROM users WHERE username = :username
                )
            )
        \'\'\', {'username': session['username']})
    codes = cursor.fetchall()
    return jsonify([row_dictionary(row) for row in codes])", 1, 3)''')
    cursor.execute('INSERT INTO users_codes (user_id, code_id) VALUES (1, 1)')