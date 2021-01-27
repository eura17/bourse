import os
import shutil
import subprocess
from time import sleep

import tarantool

from db.user import User


class TarantoolConnection:
    __work_dir = 'tarantool_work_dir'
    __migrations_dir = 'migrations'

    def __init__(self, port: int):
        self.__tarantool_subprocess = subprocess.Popen(
            ['tarantool'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        self.__port = port

    def __enter__(self):
        self.__configure(self.__port)
        self.__migrate()
        self.__tarantool_subprocess.stdin.close()
        sleep(1)
        User.set_host('localhost')
        User.set_port(self.__port)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__tarantool_subprocess.kill()

    def __configure(self, port: int):
        base_path = self.__get_base_path()
        if self.__work_dir in os.listdir(base_path):
            shutil.rmtree(self.__work_dir)
        os.mkdir(f'{base_path}/{self.__work_dir}')
        path = f'{base_path}/{self.__work_dir}'
        cfg = f'box.cfg{{listen={port}, work_dir="{path}"}}'
        self.__tarantool_subprocess.stdin.write(bytes(cfg, encoding='utf-8'))

    def __migrate(self):
        migrations = f'{self.__get_base_path()}/{self.__migrations_dir}'
        for file in os.listdir(migrations):
            with open(f'{migrations}/{file}') as f:
                self.__tarantool_subprocess.stdin.write(
                    bytes(
                        f'{f.read().strip()}\n',
                        encoding='utf-8'
                    )
                )

    @staticmethod
    def __get_base_path():
        return os.path.dirname(os.path.realpath(__file__))

    @classmethod
    def migrate(cls,
                host: str,
                port: int,
                user: str = 'admin',
                password: str = 'admin'):
        admin = tarantool.connect(host, port, user, password)
        migrations = f'{cls.__get_base_path()}/{cls.__migrations_dir}'
        for file in os.listdir(migrations):
            with open(f'{migrations}/{file}') as f:
                admin.eval(f.read().strip())
        User.set_host(host)
        User.set_port(port)
