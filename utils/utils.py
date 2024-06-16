import os
from shutil import rmtree
from datetime import datetime

def make_timestamp():
  dt = datetime.now()
  timestamp = f"{dt.year}_{dt.month}_{dt.day}_{dt.hour}_{dt.minute}_{dt.second}"
  return timestamp


def mkdir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def rmdir(path: str):
    if os.path.exists(path):
        rmtree(path)

def reinit_dir(path: str):
    rmdir(path)
    mkdir(path)


class_id2danger = {
    0:True,
    1:False,
    2:False,
    3:False,
    4:True,
}