from os.path import join, isdir, islink, splitext, abspath, exists, basename
from pathquery import exceptions
from fnmatch import fnmatch
from path import Path
from os import walk
from copy import copy


class Pattern(object):
    def __init__(self):
        self.is_directory = None
        self.is_symlink = None
        self.but_not = []
        self.glob = None
        self.ext = None
        self.named = None

    def match(self, filename_in_dir, full_filename):
        is_match = True

        if self.is_directory is not None:
            if self.is_directory != isdir(full_filename):
                is_match = False
        if self.is_symlink is not None:
            if self.is_symlink != islink(full_filename):
                is_match = False
        if self.glob is not None:
            if not fnmatch(filename_in_dir, self.glob):
                is_match = False
        if self.named is not None:
            if basename(filename_in_dir) != self.named:
                is_match = False
        if self.ext is not None:
            if splitext(full_filename)[1] != ".{0}".format(self.ext):
                is_match = False

        return is_match


class pathquery(object):
    """
    PathQuery represents a lazily executed search for files.

    Usage::
      for filepath in pathquery('yourpath/'):
          filepath.chmod("777")
    """
    def __init__(self, path):
        self._path = abspath(path)
        if not exists(self._path):
            raise exceptions.PathDoesNotExist(self._path)
        if not isdir(self._path):
            raise exceptions.PathIsNotDirectory(self._path)
        self._pattern = Pattern()
        self._but_not = []

    def is_dir(self):
        new_pathq = copy(self)
        new_pathq._pattern.is_directory = True
        return new_pathq

    def is_not_dir(self):
        new_pathq = copy(self)
        new_pathq._pattern.is_directory = False
        return new_pathq

    def is_symlink(self):
        new_pathq = copy(self)
        new_pathq._pattern.is_symlink = True
        return new_pathq

    def is_not_symlink(self):
        new_pathq = copy(self)
        new_pathq._pattern.is_symlink = False
        return new_pathq

    def glob(self, text):
        new_pathq = copy(self)
        new_pathq._pattern.glob = text
        return new_pathq

    def named(self, text):
        new_pathq = copy(self)
        new_pathq._pattern.named = text
        return new_pathq

    def ext(self, extension):
        """
        Match files with an extension - e.g. 'js', 'txt'
        """
        new_pathq = copy(self)
        new_pathq._pattern.ext = extension
        return new_pathq

    def __sub__(self, paths):
        assert isinstance(paths, pathquery), "{0} must be pathquery object.".format(paths)
        new_pathq = copy(self)
        new_pathq._but_not.append(paths)
        return new_pathq

    def __copy__(self):
        new_pathq = pathquery(self._path)
        new_pathq._pattern = copy(self._pattern)
        new_pathq._but_not = copy(self._but_not)
        return new_pathq

    def _is_match(self, root, filename_in_dir):
        full_filename = join(root, filename_in_dir)
        is_match = True
        for but_not in self._but_not:
            if but_not._is_match(filename_in_dir, full_filename)\
              and full_filename.startswith(but_not._path):
                is_match = False
        if not self._pattern.match(filename_in_dir, full_filename):
            is_match = False
        return is_match

    def __iter__(self):
        for root, dirnames, filenames_in_dir in walk(self._path):
            if self._is_match(root, ""):
                yield Path(root)
            for filename_in_dir in filenames_in_dir:
                if self._is_match(root, filename_in_dir):
                    yield Path(join(root, filename_in_dir))
