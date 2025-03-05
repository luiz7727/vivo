import ping3
import psutil


def getRAM():
    ramfd = psutil.virtual_memory()
    info = {
        "used": ramfd.used / (1024**2),
        "total": ramfd.total / (1024**2),
    }

    return info, True


def ping(server):
    try:
        response_time = ping3.ping(server)
        if response_time is not None:
            return response_time * 1000, True
        else:
            return 1000, False
    except Exception as e:
        return -1, False
