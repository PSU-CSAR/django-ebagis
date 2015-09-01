from __future__ import absolute_import
from contextlib import contextmanager



@contextmanager
def tempdirectory(suffix="", prefix="", dir=None):
    """A context manager for creating a temporary directory
    that will automatically be removed when it is no longer
    in context."""
    from tempfile import mkdtemp
    from shutil import rmtree
    tmpdir = mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        yield tmpdir
    except Exception as e:
        raise e
    finally:
        rmtree(tmpdir)
        pass


def get_path_from_tempdir(tempdir):
    import os
    tempdircontents = os.listdir(tempdir)

    directories = []
    for item in tempdircontents:
        item = os.path.join(tempdir, item)
        if os.path.isdir(item):
            directories.append(item)

    if len(directories) == 1:
        path = directories[0]
    else:
        path = tempdir

    return path

