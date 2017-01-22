class PathQueryException(Exception):
    pass


class PathDoesNotExist(Exception):
    def __init__(self, path):
        super(PathDoesNotExist, self).__init__((
            "Path '{0}' does not exist."
        ).format(path))


class PathIsNotDirectory(Exception):
    def __init__(self, path):
        super(PathIsNotDirectory, self).__init__((
            "Path '{0}' is not directory so you cannot search inside it."
        ).format(path))
