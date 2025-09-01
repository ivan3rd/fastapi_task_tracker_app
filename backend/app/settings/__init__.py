import os

DATABASE_USER = os.getenv('POSTGRES_USER', 'postgres')
DATABASE_NAME = os.getenv('POSTGRES_DB', '')
DATABASE_URL = os.getenv('DATABASE_URL', '')
DATABASE_URL_FULL = DATABASE_URL + DATABASE_NAME
APP_ADMIN_USERNAME = os.getenv('APP_ADMIN_USERNAME', 'admin')
APP_ADMIN_PASSWORD = os.getenv('APP_ADMIN_PASSWORD', 'password')

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_secret_key')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
