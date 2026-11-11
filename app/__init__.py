from flask import Flask

from app.config import get_settings
from app.dashboard import dashboard_bp
from app.routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.register_blueprint(dashboard_bp)
    return app


application = create_app()


if __name__ == "__main__":
    settings = get_settings()
    application.run(host=settings.app_host, port=settings.app_port)
