import os
from shutil import rmtree


def mkdir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def rmdir(path: str):
    if os.path.exists(path):
        rmtree(path)