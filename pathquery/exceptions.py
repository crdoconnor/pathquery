class PathQueryException(Exception):
    pass


class PathDoesNotExist(PathQueryException):
    def __init__(self, path):
        super(PathDoesNotExist, self).__init__((
            "Path '{0}' does not exist."
        ).format(path))


class PathIsNotDirectory(PathQueryException):
    def __init__(self, path):
        super(PathIsNotDirectory, self).__init__((
            "Path '{0}' is not directory so you cannot search inside it."
        ).format(path))
