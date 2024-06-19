import asyncio

from PyQt5.QtCore import QObject

from worker import Worker

class WorkerController(QObject):
    def __init__(self):
        super().__init__()
        self.worker_thread = None

    async def start_thread(self):
        if self.worker_thread is None or not self.worker_thread.isRunning():
            if self.worker_thread is not None:
                self.worker_thread.stop()
                self.worker_thread.wait()
                self.worker_thread.deleteLater()
                
            self.worker_thread = Worker()
            self.worker_thread.start()
            
            while self.worker_thread.isRunning():
                await asyncio.sleep(0.1)
