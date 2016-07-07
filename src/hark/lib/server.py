from typing import Any, Dict, Callable

import gunicorn.app.base

# Type signature for the web app handler
AppHandler = Callable[[Dict[str, Any], Callable[[bytes], None]], None]


class UnicornApp(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options={}):
        self.options = options
        self.application = app
        super(UnicornApp, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


class HTTPServer(object):
    "A Hark HTTP server"

    def __init__(
            self,
            app: AppHandler,
            port: int, workers: int):
        options = {
            'bind': '%s:%d' % ('127.0.0.1', port),
            'workers': workers,
        }

        self.gunicorn = UnicornApp(app, options)

    def run(self):
        self.gunicorn.run()
