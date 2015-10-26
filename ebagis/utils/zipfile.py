from __future__ import absolute_import


def zip_directory(directory_path, zip_path):
    """Takes an input directory path and an output zip path
    and zips the contents of the directory into a zipfile at
    output path location. The name of the output zipfile
    should be included in the zip_path argument."""
    import os
    import zipfile
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for f in files:
                rel_dir = os.path.relpath(root, directory_path)
                # first arg is file to zip (root/f), and the
                # second arg is the archive name (rel_dir/f)
                # (second arg is path realtive to the root of the AOI
                # to keep whole higher level directory structure from
                # getting zipped)
                zipf.write(os.path.join(root, f), os.path.join(rel_dir, f))
            # NEED TO USE THIS FOR EMPTY DIRS
            #for d in dirs:
              #  zips.writestr(zipfile.ZipInfo('empty/'), '')
    return zip_path


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
