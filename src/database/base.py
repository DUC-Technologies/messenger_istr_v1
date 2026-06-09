# src/database/base.py
# Импортируем реестр
from database.session import Base

# Импортируем ВСЕ модели, чтобы они зарегистрировались в Base.metadata
from auth.models import User
from messenger.db.sqlalchemy.models import Topic, Message
