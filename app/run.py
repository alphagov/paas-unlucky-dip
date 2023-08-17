import multiprocessing
import os

import uvicorn
from gunicorn.app.wsgiapp import WSGIApplication


class StandaloneApplication(WSGIApplication):
    def __init__(self, app_module: str, *, options=None):
        self.options = options or {}
        self.app_uri = app_module
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)


def dev():
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
        env_file=".env",
        reload_excludes=["app/run.py"],
    )


def prod():
    try:
        port = os.environ["PORT"]
    except KeyError as exc:
        raise KeyError("PORT environment variable not set") from exc

    StandaloneApplication(
        "app.main:app",
        options={
            "bind": f"{os.getenv('HOST', '0.0.0.0')}:{port}",
            "workers": (multiprocessing.cpu_count() * 2) + 1,
            "worker_class": "uvicorn.workers.UvicornWorker",
        },
    ).run()


def local_prod():
    from dotenv import load_dotenv  # pylint: disable=import-outside-toplevel

    load_dotenv()
    os.environ.update(
        {
            "HOST": "127.0.0.1",  # stops macos from asking for permission
            "PORT": "8000",
        }
    )
    prod()


if __name__ == "__main__":
    target = os.getenv("TARGET", "prod")
    match target:
        case "dev":
            dev()
        case "prod":
            prod()
        case "local_prod":
            local_prod()
        case _:
            raise ValueError(f"Unknown target: {target}")
