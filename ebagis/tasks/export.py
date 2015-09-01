from __future__ import absolute_import
from celery import shared_task
import os

from .models.download import Download

from .utilities import tempdirectory, zip_directory

from .settings import TEMP_DIRECTORY, DOWNLOADS_DIRECTORY


@shared_task
def export_data(download_id):
    download = Download.objects.get(pk=download_id)
    out_dir = os.path.join(DOWNLOADS_DIRECTORY, download_id)
    os.makedirs(out_dir)

    print download.querydate

    with tempdirectory(prefix="AOI_", dir=TEMP_DIRECTORY) as tempdir:
        temp_aoi_dir = download.content_object.export(
            tempdir,
            querydate=download.querydate
        )

        zip_dir = os.path.join(out_dir,
                               os.path.basename(temp_aoi_dir) + ".zip")

        download.file = zip_directory(temp_aoi_dir, zip_dir)

    download.save()
    return download.id

