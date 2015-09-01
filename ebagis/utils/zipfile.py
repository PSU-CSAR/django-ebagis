


def unzipfile(zipf, unzipdir):
    """
    """
    from zipfile import ZipFile, BadZipfile

    with ZipFile(zipf) as zfile:
        files = zfile.namelist()

        # ensure zipfile integrity
        if zfile.testzip():
            raise BadZipfile("Upload zipfile has errors." +
                             " Please try resubmitting your request.")

        # validate zfile members: make sure no problem char in names
        if not files:
            raise BadZipfile("Upload zipfile is empty.")
        else:
            for filename in files:
                if filename.startswith("/") or \
                        filename.startswith("\\") or ".." in filename:
                    raise BadZipfile("Uplaod zipfile contains nonstandard" +
                                     " filenames and cannot be opened.")

        zfile.extractall(path=unzipdir)

