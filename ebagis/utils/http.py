from __future__ import absolute_import
import logging
import os
import re
import mimetypes

from django.http import StreamingHttpResponse

from rest_framework import status
from rest_framework.response import Response

from ..constants import CHUNK_SIZE

from .filesystem import FileWrapper


logger = logging.getLogger(__name__)


def stream_file(file_path, request):
    #import pdb; pdb.set_trace()

    file_size = os.path.getsize(file_path)
    start, end = 0, None

    if "HTTP_RANGE" in request.META:
        try:
            start, end = re.findall(r"/d+", request.META["HTTP_RANGE"])
        except TypeError:
            logger.exception(
                "Malformed HTTP_RANGE in download request: {}"
                .format(request.META["HTTP_RANGE"])
            )
            return Response(
                status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
            )

        if start > end or end > file_size:
            return Response(
                status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
            )

    fwrapper = FileWrapper(
        open(file_path, 'rb'),
        blksize=CHUNK_SIZE,
        start=start,
        end=end
    )
    response = StreamingHttpResponse(
        fwrapper,
        content_type=mimetypes.guess_type(file_path)[0]
    )
    name = os.path.basename(file_path)
    response["Content-Disposition"] = \
        'attachment; filename="' + name + '"'
    response["Content-Length"] = file_size
    response["Accept-Ranges"] = 'bytes'

    if "HTTP_RANGE" in request.META:
        response["status"] = 206
        response["Content-Range"] = "bytes {}-{}/{}".format(start,
                                                            end,
                                                            file_size)

    return response
