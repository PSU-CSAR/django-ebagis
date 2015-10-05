from __future__ import absolute_import
from contextlib import contextmanager


def generate_postfix(iteration, sequential=False):
    """used to generate the postfixes for the
    make_unique_directory function"""
    from .misc import random_string
    # a sequential postfix uses integers
    if sequential:
        postfix = "_" + iteration
    else:
        # otherwise we append a unique string
        # the length of the string is 4 char,
        # but increases by 1 every 100 iterations
        length = 4 + (1 * (iteration % 100))
        postfix = "_" + random_string(length)
    return postfix


def make_unique_directory(name, path,
                          limit=None,
                          sequential_postfix=False,
                          always_append=False):
    """Iterate though postfixes to a directory name until
    the name is unique and the directory can be created. If
    the original name is unique no postfix will be appended,
    unless the always_append option is set to True, in which
    case a postfix will be appended, even if the name was
    already unique.

    User can set a limit value to stop trying to create the
    directory after that many failed attempts. The default is
    to run an unlimited number of times.

    User can also choose to use a sequential postfix, which
    appends an integer to the file name, starting with 1, and
    increments the integer until the limit is reached. Note that
    combining the sequential_postfix and always_append options
    will not start at 1, but at 0. The default behavior is to use
    a random string which is minimally 4 characters. Every 100
    iterations the string will add an extra letter to attempt to
    avoid collisions and make the directory more quickly.

    The two required arguments to this function are name and path,
    which are both strings. Name will be used as the starting point
    for the name of the directory to be created, and path is the
    location at which the directory should be created. That is,
    with a name of `bar` and a path of `/home/foo/`, the function
    will attempt to create the directory `/home/foo/bar`, appending
    a postfix as desribed above until the directory can be created."""
    import os
    from exceptions import LimitError

    # if no limit then set to True so while loop will never stop
    if limit is None:
        limit = True
    # if limit is a postive integer, don't need to do anything
    elif type(limit) == int and limit > 0:
        pass
    # if limit is neither of these then we don't know what to do
    else:
        raise TypeError("limit is not positive integer or None. Unable to proceed")

    # postfix starts as empty string unless always_append is True
    postfix = ""
    if always_append is True:
        postfix = generate_postfix(0, sequential_postfix)

    # iterate through names until directory is created
    iteration = 0
    while limit:
        iteration += 1

        # append postfix and create full directory path
        uniqueid = name + postfix
        outdirectory = os.path.join(path, uniqueid)

        # if the directory is made then break the while loop
        # so the function will return. Failure will result in
        # an exception caught by the try, which will indicate
        # the loop needs to continue.
        try:
            os.mkdir(outdirectory)
            break
        except OSError:
            pass

        # if limit is an integer, then we need to subtract one
        # then we need to check if limit is now 0. If so,
        # we need to raise an exception indicating failure.
        if not limit is True:
            limit -= 1
            if limit <= 0:
                raise LimitError("Postfix limit was reached before directory could be created.")

        # generate the next postfix based on the iteration
        postfix = generate_postfix(iteration, sequential_postfix)

    return uniqueid, outdirectory


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

