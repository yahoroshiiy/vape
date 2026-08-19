import mimetypes
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.wsgi import application as django_application
STATIC_DIRS = [BASE_DIR / "static", BASE_DIR / "shop" / "static"]

class StaticMiddleware:
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path.startswith("/static/"):
            rel = path[len("/static/"):].lstrip("/")
            for static_dir in STATIC_DIRS:
                root = static_dir.resolve()
                candidate = (static_dir / rel).resolve()
                try:
                    candidate.relative_to(root)
                except ValueError:
                    continue
                if candidate.is_file():
                    data = candidate.read_bytes()
                    ctype = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
                    start_response("200 OK", [("Content-Type", ctype), ("Content-Length", str(len(data))), ("Cache-Control", "public, max-age=86400")])
                    return [data]
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"Not Found"]
        return self.app(environ, start_response)

app = StaticMiddleware(django_application)
application = app
