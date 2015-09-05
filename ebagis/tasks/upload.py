from __future__ import absolute_import
from celery import shared_task

from django.contrib.contenttypes.models import ContentType

from ..models.upload import Upload

from ..utils.filesystem import tempdirectory, get_path_from_tempdir
from ..utils.zipfile import unzipfile

from ..settings import TEMP_DIRECTORY


@shared_task
def process_upload(upload_id):

    upload = Upload.objects.get(pk=upload_id)
    upload_class = ContentType.model_class(upload.content_type)
    zip_path = upload.file

    temp_prefix = upload_class.__name__ + "_"

    with tempdirectory(prefix=temp_prefix, dir=TEMP_DIRECTORY) as tempdir:
        print "Extracting upload zip to {}.".format(tempdir)
        unzipfile(zip_path, tempdir)

        temp_path = get_path_from_tempdir(tempdir)

        print "Upload to import is {}.".format(temp_path)

    if upload.is_update:
        imported_obj = upload_class.update(upload, temp_path)
    elif not upload.is_update:
        imported_obj = upload_class.create_from_upload(upload, temp_path)
    else:
        raise Exception("Unexpected fatal error: is_update not set on upload")

    return "{},{}".format(imported_obj.id,upload.content_type)

