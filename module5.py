from multiprocessing.shared_memory import SharedMemory
from multiprocessing import Lock
import struct

SHM_NAME = "preference_state"
Lock = Lock()

def init():
    try:
        shm = SharedMemory(name=SHM_NAME)
    except FileNotFoundError:
        shm = SharedMemory(name=SHM_NAME,create=True,size=12)
        shm.buf[:12] = struct.pack('iii',0,0,0)
    return shm
            
_shm = init()

def read_state():
    with Lock:
        good,mid,bad = struct.unpack('iii', _shm.buf[:12])
    return {'good': good, 'mid': mid, 'bad': bad}

def write_state(good,mid,bad):
    with Lock:
        _shm.buf[:12] = struct.pack('iii',good,mid,bad)