import os
import shutil
import subprocess
from time import sleep

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
        if self.__tarantool_subprocess is not None:
            base_path = self.__get_base_path()
            path = f'{base_path}/{self.__migrations_dir}'
            migrations = ''
            for file in os.listdir(path):
                with open(f'{path}/{file}') as f:
                    migrations += f'{f.read().strip()}\n\n\n'
            self.__tarantool_subprocess.stdin.write(bytes(migrations,
                                                          encoding='utf-8'))

    @staticmethod
    def __get_base_path():
        return os.path.dirname(os.path.realpath(__file__))
