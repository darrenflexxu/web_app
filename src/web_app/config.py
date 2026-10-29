from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    max_upload_size_bytes: int = 5 * 1024 * 1024  # 5 MB
    
    posts_per_page: int = 10
    
    reset_token_expire_minutes: int = 60
     
    mail_server: str = "localhost"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True
    
    frontend_url: str = "http://localhost:8000"

    # Backblaze B2 (S3-compatible API)
    b2_key_id: str = ""
    b2_application_key: SecretStr = SecretStr("")
    b2_bucket: str = ""
    b2_region: str = ""  # e.g. us-west-004
    b2_endpoint_url: str = ""  # e.g. https://s3.us-west-004.backblazeb2.com
    # Public bucket URL, e.g. https://f004.backblazeb2.com/file/<bucket>
    b2_public_url: str = ""
    b2_profile_pics_prefix: str = "profile_pics"
    # Private bucket: serve images via short-lived presigned URLs.
    b2_private_bucket: bool = False
    b2_presigned_url_expires_seconds: int = 3600


settings = Settings()
