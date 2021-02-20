import os
from shutil import rmtree
from subprocess import Popen, PIPE
from time import sleep

import tarantool

from db.user import User


class TarantoolConnection:
    __work_dir = 'tarantool_work_dir'
    __migrations_dir = 'migrations'

    def __init__(self, port: int):
        self.__tarantool_subprocess = Popen(
            ['tarantool'],
            stdin=PIPE,
            stdout=PIPE
        )
        self.__host = 'localhost'
        self.__port = port

    def __enter__(self) -> None:
        self.__configure(self.__port)
        self.__migrate()
        self.__tarantool_subprocess.stdin.close()
        sleep(1)
        User.set_host(self.__host)
        User.set_port(self.__port)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__tarantool_subprocess.kill()
        rmtree(self.__get_work_dir())

    def __configure(self, port: int) -> None:
        base_path = self.__get_base_path()
        working_path = self.__get_work_dir()
        if self.__work_dir in os.listdir(base_path):
            rmtree(working_path)
        os.mkdir(working_path)
        cfg = f'box.cfg{{listen={port}, work_dir="{working_path}"}}'
        self.__tarantool_subprocess.stdin.write(bytes(cfg, encoding='utf-8'))

    def __migrate(self) -> None:
        migrations = self.__get_migrations_dir()
        for file in sorted(os.listdir(migrations)):
            with open(os.path.join(migrations, file)) as f:
                self.__tarantool_subprocess.stdin.write(
                    bytes(
                        f'{f.read().strip()}\n',
                        encoding='utf-8'
                    )
                )

    @staticmethod
    def __get_base_path() -> str:
        return os.path.dirname(os.path.realpath(__file__))

    @classmethod
    def __get_migrations_dir(cls) -> str:
        return os.path.join(cls.__get_base_path(), cls.__migrations_dir)

    @classmethod
    def __get_work_dir(cls):
        return os.path.join(cls.__get_base_path(), cls.__work_dir)

    @classmethod
    def migrate(cls,
                host: str,
                port: int,
                user: str = 'admin',
                password: str = 'admin') -> None:
        admin = tarantool.connect(host, port, user, password)
        migrations_dir = cls.__get_migrations_dir()
        for file in sorted(os.listdir(migrations_dir)):
            with open(os.path.join(migrations_dir, file)) as f:
                admin.eval(f.read().strip())
        User.set_host(host)
        User.set_port(port)
