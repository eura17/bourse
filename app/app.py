import asyncio
import logging
import signal
import sys
from logging import getLogger

from quart import Quart


class App:
    api: Quart
    loop: asyncio.AbstractEventLoop
    shutdown_event: asyncio.Event
    logger: logging.Logger

    def __init__(self, name: str) -> None:
        self._setup_logger(name)
        self.api = Quart(name)
        self.shutdown_event = asyncio.Event()
        self.loop = asyncio.get_event_loop()

    def _setup_logger(self, name: str) -> None:
        self.logger = getLogger(name)
        sysoutHandler = logging.StreamHandler(sys.stdout)
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        sysoutHandler.setFormatter(logFormatter)
        self.logger.addHandler(sysoutHandler)
        self.logger.setLevel(level=logging.INFO)

    def run(self, host: str = '127.0.0.1',
            port: int = 5000) -> None:
        #signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)

        #for s in signals:
        #    self.loop.add_signal_handler(s, lambda: asyncio.create_task(self.stop()))

        try:
            self.loop.create_task(self.api.run_task(host=host, port=port,
                                                    shutdown_trigger=self.shutdown_event.wait))
            self.loop.run_forever()
        finally:
            self.loop.close()

    async def stop(self) -> None:
        self.logger.info('shutting down...')
        self.shutdown_event.set()
        tasks = [task for task in asyncio.all_tasks() if task is not
                 asyncio.current_task()]
        list(map(lambda task: task.cancel(), tasks))

        await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.info('shut down')

        self.loop.stop()
