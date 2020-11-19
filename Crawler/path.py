import os 
from pathlib import Path
import platform
osName = platform.platform().split('-')[0]

class pharsePath():
    def __init__(self, PATH):
        self.base = PATH['base']
        self.data = PATH['data']
        self.iput = PATH['iput']
        self.oput = PATH['oput']

class pharseName():
    def __init__(self, NAME):
        self.kwch = NAME['kwch']
        self.kwen = NAME['kwen']
        self.oput = NAME['oput']

class path():
    def __init__(self):
        PATH = {}
        PATH['base'] = Path(os.path.abspath(__file__)).parents[0]
        PATH['data'] = os.path.join(PATH['base'], 'DATA')
        PATH['iput'] = os.path.join(PATH['base'], 'DATA', 'ReadData')  
        PATH['oput'] = os.path.join(PATH['base'], 'DATA', 'outNews', 'NEWS')  

        NAME = {}
        NAME['kwch'] = os.path.join(PATH['iput'], 'SearchKeyword.xls')
        NAME['kwen'] = os.path.join(PATH['iput'], 'SearchKeyword_eng.xls')
        NAME['oput'] = os.path.join(PATH['oput'], 'TIME.xls')

        self.PATH = pharsePath(PATH)
        self.NAME = pharseName(NAME)
            
if __name__ == '__main__':
    p = path()
