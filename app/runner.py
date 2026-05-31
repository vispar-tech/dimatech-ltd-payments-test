from typing import Any

from gunicorn.app.base import BaseApplication
from gunicorn.util import import_app
from uvicorn.workers import UvicornWorker as BaseUvicornWorker


class UvicornWorker(BaseUvicornWorker):
    """
    Configuration for uvicorn workers.

    This class is subclassing UvicornWorker and defines
    some parameters class-wide, because it's impossible,
    to pass these parameters through gunicorn.
    """

    CONFIG_KWARGS: dict[str, Any] = {  # noqa: RUF012
        "loop": "uvloop",
        "http": "httptools",
        "lifespan": "on",
        "factory": True,
        "proxy_headers": False,
    }


class GunicornApplication(BaseApplication):  # type: ignore[misc]
    """
    Custom gunicorn application.

    This class is used to start guncicorn
    with custom uvicorn workers.
    """

    def __init__(
        self,
        app: str,
        host: str,
        port: int,
        workers: int,
        **kwargs: Any,
    ) -> None:
        """Initialize GunicornApplication with app and server settings."""
        self.options: dict[str, Any] = {
            "bind": f"{host}:{port}",
            "workers": workers,
            "worker_class": "app.runner.UvicornWorker",
            **kwargs,
        }
        self.app = app
        super().__init__()  # type: ignore

    def load_config(self) -> None:
        """
        Load config for web server.

        This function is used to set parameters to gunicorn
        main process. It only sets parameters that
        gunicorn can handle. If you pass unknown
        parameter to it, it crash with error.
        """
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:  # type: ignore
                self.cfg.set(key.lower(), value)  # type: ignore

    def load(self) -> object:
        """
        Load actual application.

        Gunicorn loads application based on this
        function's returns. We return python's path to
        the app's factory.

        :returns: python path to app factory.
        """
        return import_app(self.app)
