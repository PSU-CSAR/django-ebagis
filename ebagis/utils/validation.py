from __future__ import absolute_import
import os

import arcpy

from .constants import AOI_RASTER_LAYER, AOI_GDB, REQUIRED_LAYERS


def validate_required_gdb_layers(gdb_path, required_layers):
    """
    """
    errorlist = []

    if not arcpy.Exists(gdb_path):
        errorlist.append("Geodatabase {} does not exist in AOI."
                         .format(os.path.basename(gdb_path)))
    else:
        if required_layers:
            for layer, layertype in required_layers:
                try:
                    if not arcpy.Describe(
                        os.path.join(gdb_path,
                                     layer)
                    ).DataType == layertype:
                        errorlist.append(
                            "Layer {} is not required type {}.".format(
                                os.path.join(os.path.basename(gdb_path),
                                             layer),
                                layertype
                                )
                        )
                except IOError:
                    errorlist.append(
                        "Layer {} was not found.".format(
                            os.path.join(os.path.basename(gdb_path), layer)
                            )
                    )

    return errorlist


def validate_aoi(aoi_path):
    """
    """
    errorlist = []

    # check to see that path is valid
    if not arcpy.Exists(aoi_path):
        errorlist.append("AOI path is not valid.")
        return errorlist

    # check for aoi boundary raster layer
    # must be separate as multiple names possible
    found = False
    for layer in AOI_RASTER_LAYER[0]:
        try:
            found = found or (arcpy.Describe(
                os.path.join(aoi_path, AOI_GDB, layer))
                .DataType == AOI_RASTER_LAYER[1])
        except IOError:
            pass

    if not found:
        errorlist.append("Raster AOI boundary was not found."
                         .format(os.path.join(os.path.basename(aoi_path),
                                              AOI_GDB,
                                              layer)))

    # check for required gdbs and their required layers
    for gdb, required_layers in REQUIRED_LAYERS.iteritems():
        errorlist += validate_required_gdb_layers(os.path.join(aoi_path, gdb),
                                                  required_layers)

    return errorlist

