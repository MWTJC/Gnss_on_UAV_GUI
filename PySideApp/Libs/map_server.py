from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

from PySide6.QtCore import QThread, Signal
from loguru import logger

class ServerThread(QThread):
    shutdown_complete = Signal()

    def __init__(self, server):
        super().__init__()
        self.server = server

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()
        self.shutdown_complete.emit()

class LocalServer:
    def __init__(self, dir, port=28000, daemon=True):
        self.port = port
        Handler = partial(SimpleHTTPRequestHandler, directory=dir)
        self.server = HTTPServer(('localhost', port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=daemon)

    def start(self):
        self.thread.start()
        logger.success('map server started...')

    def stop(self):
        self.server.shutdown()
        self.thread.join()
        logger.success('map server stopped...')


if __name__ == "__main__":
    server = LocalServer(port=28000, daemon=False, dir="./")
    server.start()
