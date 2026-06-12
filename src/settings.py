from dotenv import load_dotenv
from envparse import Env

load_dotenv(override=False)

env = Env()

AUTH_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
)

AUTH_APP_PORT = env.int("APP_PORT", default=40610)

# AUTH
AUTH_SECRET_KEY: str = env.str("SECRET_KEY", default="secret_key")
AUTH_ALGORITHM: str = env.str("ALGORITHM", default="HS256")
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)

# MESSENGER
MESSENGER_APP_PORT = env.int("MESSENGER_APP_PORT", default=46020)

# S3 / MinIO
S3_ENDPOINT_URL: str = env.str("S3_ENDPOINT_URL", default="http://localhost:9000")
S3_ACCESS_KEY: str = env.str("S3_ACCESS_KEY", default="minioadmin")
S3_SECRET_KEY: str = env.str("S3_SECRET_KEY", default="minioadmin")
S3_BUCKET_REPORTS: str = env.str("S3_BUCKET_REPORTS", default="reports")
S3_PRESIGNED_URL_EXPIRES: int = env.int("S3_PRESIGNED_URL_EXPIRES", default=3600)
