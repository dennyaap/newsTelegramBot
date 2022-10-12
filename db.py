import sqlite3

class BotDB:
    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connect.cursor()
        
    def find_user(self, user_id):
        result = self.cursor.execute("SELECT id FROM users WHERE id = ?", (user_id, ))
        return bool(len(result.fetchall()))

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
        return self.connect.commit()

    def get_news_categories(self):
        result = self.cursor.execute("SELECT * FROM categories")
        return result.fetchall()

    def get_category(self, category_id):
        result = self.cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id, ))
        return result.fetchone()
    
    def check_subscribe_category(self, user_id, category_id):
        result = self.cursor.execute("SELECT category_id FROM subscribes WHERE user_id = ? AND category_id = ?", (user_id, category_id,))
        return bool(len(result.fetchall()))

    def subscribe_category(self, user_id, category_id):
        self.cursor.execute("INSERT INTO subscribes (user_id, category_id) VALUES (?, ?)", (user_id, category_id))
        return self.connect.commit()

    def get_subscribes(self, user_id):
        result = self.cursor.execute("SELECT category_id, name FROM subscribes INNER JOIN categories ON categories.id = subscribes.category_id WHERE user_id = ?", (user_id,))
        return result.fetchall()
        
    def unsubscribe_category(self, user_id, category_id):
        self.cursor.execute("DELETE FROM subscribes WHERE user_id = ? AND category_id = ?", (user_id, category_id,))
        return self.connect.commit()