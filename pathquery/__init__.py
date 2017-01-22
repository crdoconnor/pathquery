from os.path import join, isdir, islink, splitext, abspath, exists
from pathquery import exceptions
from fnmatch import fnmatch
from path import Path
from os import walk
import copy


class pathq(object):
    """
    PathQuery represents a lazily executed search for files.

    Usage::
      for filepath in pathq('yourpath/'):
        filepath.chmod("777")
    """
    def __init__(self, path):
        self._path = abspath(path)
        if not exists(self._path):
            raise exceptions.PathDoesNotExist(self._path)
        if not isdir(self._path):
            raise exceptions.PathIsNotDirectory(self._path)
        self._is_directory = None
        self._is_symlink = None
        self._but_not = []
        self._glob = None
        self._ext = None

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

    def glob(self, text):
        new_pathq = copy.copy(self)
        new_pathq._glob = text
        return new_pathq

    def ext(self, extension):
        """
        Match files with an extension - e.g. 'js', 'txt'
        """
        new_pathq = copy.copy(self)
        new_pathq._ext = extension
        return new_pathq

    def _is_match(self, full_filename):
        is_match = True
        for but_not in self._but_not:
            if but_not._path in full_filename:
                is_match = False
        if self._is_directory is not None:
            if self._is_directory != isdir(full_filename):
                is_match = False
        if self._is_symlink is not None:
            if self._is_symlink != islink(full_filename):
                is_match = False
        if self._glob is not None:
            if not fnmatch(full_filename, self._glob):
                is_match = False
        if self._ext is not None:
            if splitext(full_filename)[1] != ".{0}".format(self._ext):
                is_match = False
        return is_match

    def __iter__(self):
        for root, dirnames, filenames_in_dir in walk(self._path):
            if self._is_match(root):
                yield Path(root)
            for filename_in_dir in filenames_in_dir:
                full_filename = join(root, filename_in_dir)
                if self._is_match(full_filename):
                    yield Path(full_filename)
