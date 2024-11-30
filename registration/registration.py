import unittest
import sqlite3
import os
import re

DB_NAME = 'users_test.db'

def create_db():
    """Создаем базу данных и таблицу users, если она не существует."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

def is_valid_email(email):
    """Проверяем, что email имеет корректный формат."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def add_user(username, email, password):
    """Добавляем пользователя в базу данных, если данные корректные."""
    if not username or not email or not password or not is_valid_email(email):
        return False
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception:
        return False

def authenticate_user(username, password):
    """Аутентифицируем пользователя по имени и паролю."""
    if not username or not password:
        return False
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        return cursor.fetchone() is not None

def display_users():
    """Возвращаем список пользователей из базы данных."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, email FROM users')
        users = cursor.fetchall()
        return users if users else []

class TestUserDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Создаем базу данных перед запуском тестов
        create_db()

    @classmethod
    def tearDownClass(cls):
        # Удаляем тестовую базу данных после всех тестов
        try:
            os.remove(DB_NAME)
        except Exception as e:
            print(f"Error deleting database: {e}")

    def test_add_user_success(self):
        """Тест успешного добавления пользователя."""
        self.assertTrue(add_user("validuser", "user@example.com", "password123"))

    def test_add_user_duplicate(self):
        """Тест добавления пользователя с существующим логином."""
        self.assertTrue(add_user("duplicateuser", "duplicate@example.com", "password123"))
        self.assertFalse(add_user("duplicateuser", "newemail@example.com", "newpassword"))

    def test_add_user_empty_username(self):
        """Тест добавления пользователя с пустым логином."""
        self.assertFalse(add_user("", "test@example.com", "password123"))

    def test_add_user_empty_email(self):
        """Тест добавления пользователя с пустым email."""
        self.assertFalse(add_user("user", "", "password123"))

    def test_add_user_empty_password(self):
        """Тест добавления пользователя с пустым паролем."""
        self.assertFalse(add_user("user", "user@example.com", ""))

    def test_authenticate_user_success(self):
        """Тест успешной аутентификации пользователя."""
        add_user("testauth", "auth@example.com", "password123")
        self.assertTrue(authenticate_user("testauth", "password123"))

    def test_authenticate_user_not_exist(self):
        """Тест аутентификации несуществующего пользователя."""
        self.assertFalse(authenticate_user("nonexistentuser", "somepassword"))

    def test_authenticate_user_invalid_password(self):
        """Тест аутентификации пользователя с неправильным паролем."""
        add_user("testauth2", "auth2@example.com", "correctpassword")
        self.assertFalse(authenticate_user("testauth2", "wrongpassword"))

    def test_authenticate_user_empty_credentials(self):
        """Тест аутентификации с пустым логином и паролем."""
        self.assertFalse(authenticate_user("", ""))

    def test_display_users(self):
        """Тест отображения списка пользователей."""
        add_user("user1", "user1@example.com", "password1")
        add_user("user2", "user2@example.com", "password2")
        users = display_users()
        self.assertEqual(len(users), 2)
        self.assertIn(("user1", "user1@example.com"), users)
        self.assertIn(("user2", "user2@example.com"), users)

    def test_display_users_empty(self):
        """Тест отображения пользователей в пустой базе данных."""
        self.tearDownClass()  # Удаляем всех пользователей перед тестом
        users = display_users()
        self.assertEqual(users, [])

if __name__ == '__main__':
    unittest.main()
