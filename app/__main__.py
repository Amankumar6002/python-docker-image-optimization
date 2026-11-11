from app import application
from app.config import get_settings


if __name__ == "__main__":
    settings = get_settings()
    application.run(host=settings.app_host, port=settings.app_port)
