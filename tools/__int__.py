import os

def __set_dir__():
    curpath = os.path.abspath(__file__)
    dirpath = os.path.dirname(curpath)
    os.chdir(dirpath)
    print(f'current path {curpath}, dir path {dirpath}')
    return  dirpath
