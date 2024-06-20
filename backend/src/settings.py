SCYLLA_DB_USER = ""
SCYLLA_DB_PASSWORD = ""
SCYLLA_DB_HOST = "localhost"
SCYLLA_DB_PORT = "9042"
SCYLLA_KEYSPACE = 'dev_messenger'

MESSENGER_APP_PORT = 46020

from envparse import Env

env = Env()

###########################################################
#                       AUTH MODULE                       #
###########################################################

AUTH_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
)  # connect string for the real database
AUTH_APP_PORT = env.int("APP_PORT", default=40610)

# AUTH
AUTH_SECRET_KEY: str = env.str("SECRET_KEY", default="secret_key")
AUTH_ALGORITHM: str = env.str("ALGORITHM", default="HS256")
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)