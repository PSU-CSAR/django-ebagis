# -*- coding: utf-8 -*-

import sys
sys.path.append(r"Z:\Macintosh HD\Users\phoetrymaster\Development\CSAR\BAGIS\Database\Importer")

import os
from arcpy import ListFeatureClasses, ListRasters, ListTables, Describe
from arcpy import CopyFeatures_management, CopyRaster_management, TableToTable_conversion
from arcpy import env, ExecuteError
from utilities import generate_random_name
from constants import *


# *************** CONSTANTS ***************


# **************** CLASSES ****************

class GeodatabaseError(Exception):
    pass


class Geodatabase(object):
    """
    """
    def __init__(self, path, fcs, rasters, tables):
        """Initialize the class.

        Required:  path - path to the geodatabase
                   fcs - list of feature classes in the gdb
                   rasters - list of rasters in the gdb
                   tables - list of tables in the gdb
        """
        self.path = path
        self.featureclasses = fcs
        self.rasterlayers = rasters
        self.tables = tables

    @classmethod
    def open_GDB(self, path):
        """
        """
        workspace = env.workspace
        env.workspace = path

        self.validate_geodatabase(path)

        fcs     = ListFeatureClasses()
        rasters = ListRasters()
        tables  = ListTables()

        env.workspace = workspace

        return Geodatabase(path, fcs, rasters, tables)

    @staticmethod
    def validate_geodatabase(path):
        """
        """
        try:
            desc = Describe(path)
            assert desc.DataType == 'Workspace'
            assert desc.workspacetype == 'LocalDatabase'
        except IOError as e:
            raise GeodatabaseError(e)
        except AssertionError:
            raise GeodatabaseError("{} is not a valid geodatabase.".format(path))

    def get_layers_dict(self):
        """
        Returns a dictionary of the geodatabase layers in the format:

            {RasterType: [list], FCType: [list], TableType: [list]}

        where the types are the ESRI types, set in the constants at the
        top of this file.
        """
        return {RASTER_TYPECODE: self.rasterlayers,
                FC_TYPECODE: self.feature_class_to_shapefile,
                TABLE_TYPECODE: self.tables}

    # TODO: convert to take layer type as argument, not function, and to detect if type not supplied
    # TODO: refactor into a public method
    def _layer_to_file(self, layer, extension, outputdirectory, copy_function,
                       outname=None):
        """
        """
        while True:
            if outname:
                # generate a name of format shortname_XXXXX where XXXXX is random string
                newname = outname
            else:
                # use same name as layer
                newname = layer

            newlayer = os.path.join(outputdirectory, newname + extension)
            layer = os.path.join(self.path, layer)

            try:
                copy_function(layer, newlayer)
            except ExecuteError as e:
                # if using shortname and already exists error, try again
                if shortname and str(e).split("\n")[1].startswith("ERROR 000725"):
                    pass
                else:
                    # if not using shortname or other error, re-raise it
                    raise e
            else:
                # processed successfully, so break while loop
                break

        return newlayer

    def feature_class_to_shapefile(self, featureclass, outputdirectory,
                                   outname_to_use=None):
        """
        """
        shapefile_ext = ".shp"

        if featureclass not in self.featureclasses:
            raise GeodatabaseError("Feature class {} not found in geodatabase.".format(featureclass))

        if not outputdirectory:
            outputdirectory = env.workspace

        return self._layer_to_file(featureclass,
                                   shapefile_ext,
                                   outputdirectory,
                                   CopyFeatures_management,
                                   outname=outname_to_use)

    def feature_class_to_shapefile_multiple(self, outputdirectory,
                                            featureclasses=None,
                                            outname_to_use=None):
        """
        """
        if not featureclasses:
            featureclasses = self.featureclasses

        newfcs = []
        for fc in featureclasses:
            newfcs.append(self.feature_class_to_shapefile(fc,
                                                          outputdirectory,
                                                          outname_to_use=outname_to_use))

        return newfcs

    def raster_layer_to_file(self, rasterlayer, outputdirectory,
                             rasterformat=".img",
                             outname_to_use=None):
        """
        """
        if rasterlayer not in self.rasterlayers:
            raise GeodatabaseError("Raster layer {} not found in geodatabase.".format(rasterlayer))

        if not rasterformat.startswith("."):
            rasterformat = "." + rasterformat

        return self._layer_to_file(rasterlayer,
                                   rasterformat,
                                   outputdirectory,
                                   CopyRaster_management,
                                   outname=outname_to_use)

    def raster_layer_to_file_multiple(self, outputdirectory,
                                      rasterlayers=None,
                                      rasterformat=".img",
                                      outname_to_use=None):
        """
        """
        if not rasterlayers:
            rasterlayers = self.rasterlayers

        newrasters = []
        for raster in rasterlayers:
            newrasters.append(self.raster_layer_to_file(raster,
                                                        outputdirectory,
                                                        rasterformat,
                                                        outname_to_use=outname_to_use))

        return newrasters

    def table_to_file(self, table, outputdirectory,
                      tableformat=".dbf",
                      outname_to_use=None):
        """
        """
        if table not in self.tables:
            raise GeodatabaseError("Table {} not found in geodatabase.".format(table))

        if not tableformat.startswith("."):
            tableformat = "." + tableformat

        return self._layer_to_file(table,
                                   tableformat,
                                   outputdirectory,
                                   TableToTable_conversion,
                                   outname=outname_to_use)

    def table_to_file_multiple(self, outputdirectory,
                               tables=None,
                               tabularformat=".dbf",
                               outname_to_use=None):
        """
        """
        if not tables:
            tables = self.tables

        newtables = []
        for table in self.tables:
            newtables.append(self.table_to_file(table,
                                                outputdirectory,
                                                tabularformat,
                                                outname_to_use=outname_to_use))

        return newtables

    def all_layers_to_files(self, outputdirectory, rasterformat=".img",
                            tabularformat=".dbf"):
        """
        """
        copied = []
        copied += self.feature_class_to_shapefile_multiple(outputdirectory)
        copied += self.raster_layer_to_file_multiple(outputdirectory,
                                                     rasterformat=rasterformat)
        copied += self.table_to_file_multiple(outputdirectory,
                                              tabularformat=tabularformat)

        return copied


# *************** MAIN CHECK ***************

if __name__ == '__main__':
    pass