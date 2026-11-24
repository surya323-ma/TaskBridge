import os


class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./taskdesk.db")
        self.secret_key = os.getenv("SECRET_KEY", "change-me-in-production")
        self.algorithm = "HS256"
        self.access_token_minutes = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
        self.admin_username = os.getenv("ADMIN_USERNAME", "admin")
        self.admin_password = os.getenv("ADMIN_PASSWORD", "admin12345")
        self.seed_demo = os.getenv("SEED_DEMO", "true").lower() == "true"


settings = Settings()
