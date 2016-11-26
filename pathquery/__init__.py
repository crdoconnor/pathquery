from os.path import split, join, isdir, islink
from fnmatch import fnmatch
from path import Path
from os import walk
import copy


class pathq(object):
    def __init__(self, path):
        self._path = path
        self._head, self._tail = split(str(self._path))
        self._is_directory = None
        self._is_symlink = None
        if self._head == '':
            self._head = '.'
        self._but_not = []

    def but_not(self, paths):
        assert type(paths) is pathq
        new_pathq = copy.copy(self)
        new_pathq._but_not.append(paths)
        return new_pathq

    def is_dir(self):
        new_pathq = copy.copy(self)
        new_pathq._is_directory = True
        return new_pathq

    def is_not_dir(self):
        new_pathq = copy.copy(self)
        new_pathq._is_directory = False
        return new_pathq

    def is_symlink(self):
        new_pathq = copy.copy(self)
        new_pathq._is_symlink = True
        return new_pathq

    def is_not_symlink(self):
        new_pathq = copy.copy(self)
        new_pathq._is_symlink = False
        return new_pathq

    def _is_match(self, full_filename):
        if fnmatch(full_filename, self._tail):
            is_match = True
            for but_not in self._but_not:
                if fnmatch(full_filename, but_not._path):
                    is_match = False
            if self._is_directory is not None:
                if self._is_directory != isdir(full_filename):
                    is_match = False
            if self._is_symlink is not None:
                if self._is_symlink != islink(full_filename):
                    is_match = False
            return is_match

    def __iter__(self):
        for root, dirnames, filenames_in_dir in walk(self._head):
            if self._is_match(root):
                if root.startswith("./"):
                    root = root[2:]
                yield Path(root)
            for filename_in_dir in filenames_in_dir:
                full_filename = join(root, filename_in_dir)
                if self._is_match(full_filename):
                    if full_filename.startswith("./"):
                        full_filename = full_filename[2:]
                    yield Path(full_filename)
