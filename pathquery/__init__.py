import copy
import fnmatch
from os import walk
from os.path import split, join
from path import Path
from fnmatch import fnmatch


class pathq(object):
    def __init__(self, path):
        self._path = path
        self._head, self._tail = split(str(self._path))
        if self._head == '':
            self._head = '.'
        self._but_not = []

    def but_not(self, paths):
        assert type(paths) is pathq
        new_pathq = copy.copy(self)
        new_pathq._but_not.append(paths)
        return new_pathq

    def _all_files(self):
        matches = []
        for root, dirnames, filenames_in_dir in walk(self._head):
            for filename_in_dir in filenames_in_dir:
                full_filename = join(root, filename_in_dir)
                if fnmatch(full_filename, self._tail):
                    is_match = True
                    for but_not in self._but_not:
                        if fnmatch(full_filename, but_not._path):
                            is_match = False
                    if is_match:
                        if full_filename.startswith("./"):
                            full_filename = full_filename[2:]
                        matches.append(Path(full_filename))
        return matches

    def __iter__(self):
        return iter(self._all_files())
