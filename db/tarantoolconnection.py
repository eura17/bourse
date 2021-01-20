from typing import NoReturn
from abc import ABC
import os
import subprocess
from time import sleep


class TarantoolConnection(ABC):
    _HOST = None
    _PORT = None
    __tarantool_subprocess = None

    @classmethod
    def set_host(cls, value: str) -> NoReturn:
        cls._HOST = value

    @classmethod
    def set_port(cls, value: int) -> NoReturn:
        cls._PORT = value

    @classmethod
    def launch(cls,
               port: int) -> NoReturn:
        cls.__tarantool_subprocess = subprocess.Popen(
            ['tarantool'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        cls.__configure(port)
        cls.__migrate()
        cls.__tarantool_subprocess.stdin.close()
        sleep(1)
        cls.set_host('localhost')
        cls.set_port(port)

    @classmethod
    def __configure(cls, port: int):
        path = cls.__get_dir()
        if 'work_dir' not in os.listdir(path):
            os.mkdir(f'{path}/work_dir')
        path = f'{path}/work_dir'
        cfg = f'box.cfg{{listen={port}, work_dir="{path}"}}'
        cls.__tarantool_subprocess.stdin.write(bytes(cfg, encoding='utf-8'))

    @classmethod
    def __migrate(cls):
        if cls.__tarantool_subprocess is not None:
            path = cls.__get_dir()
            migrations = ''
            for file in os.listdir(f'{path}/migrations'):
                with open(f'{path}/migrations/{file}') as f:
                    migrations += f.read().strip()
                    migrations += '\n\n\n'
            cls.__tarantool_subprocess.stdin.write(bytes(migrations,
                                                         encoding='utf-8'))

    @staticmethod
    def __get_dir():
        return os.path.dirname(os.path.realpath(__file__))

    @classmethod
    def kill(cls):
        cls.__tarantool_subprocess.kill()
