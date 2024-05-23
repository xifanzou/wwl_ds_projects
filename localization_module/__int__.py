import os

def __set_dir__():
    curpath = os.path.abspath(__file__)
    dirpath = os.path.dirname(os.path.dirname(curpath))
    os.chdir(dirpath)
    # print(curpath, dirpath)
    return  dirpath
