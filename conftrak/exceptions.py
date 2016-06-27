

class ConfTrakException(Exception):
    pass


class ConfTrakNotFoundException(ConfTrakException, RuntimeError):
    pass
