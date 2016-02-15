from __future__ import absolute_import


def hash_file(filepath):
    import hashlib
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            block = f.read(2**10)
            if not block:
                break
            sha.update(block)
    return sha.hexdigest()


def generate_uuid(model_class):
    import uuid
    # get a list of all of this model's object IDs in the table
    # this does create a race condition, but the performance gain of
    # only hitting the DB offsets the incredibly small chance that
    # an equal UUID will be created in the time this method will run
    existing_ids = model_class.objects.values_list('id', flat=True)

    # generate UUIDs until one is created
    # that is not in the existing list
    while True:
        id = uuid.uuid4()
        if id not in existing_ids:
            break

    return id


def validate_path(path, allow_whitespace=False,
                  invalid_chars=[":", "/", "\\", "*", "?", ".", "%", "$"]):
    """Validate a user-given path to ensure it does not have any
    restricted characters that could be used for malicious intent,
    or for non-malicious intent that might result in undesired
    operation."""
    if not allow_whitespace:
        from string import whitespace
        for char in whitespace:
            if char in path:
                raise Exception("Cannot contain whitespace.")

    for char in invalid_chars:
        if char in path:
            raise Exception(
                "Cannot contain {}.".format(invalid_chars)
            )

    return path


def validate_required_gdb_layers(gdb_path, required_layers):
    """
    """
    import arcpy
    import os
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
    import os
    import arcpy
    from ..constants import AOI_RASTER_LAYER, AOI_GDB, REQUIRED_LAYERS

    errorlist = []

    # check to see that path is valid
    if not arcpy.Exists(aoi_path):
        errorlist.append("AOI path is not valid: {}".format(aoi_path))
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
