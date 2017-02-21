import requests
import json

from arcpy import Buffer_analysis, Geometry, FromWKT, SpatialReference


def gen_query_params_from_point(pointWKT, sr, dist='100 Meters'):
    point = FromWKT(pointWKT, SpatialReference(sr))
    buff = json.loads(Buffer_analysis(point, Geometry(), dist)[0].extent.JSON)
    return {
        #'text': None,
        'geometry': '{},{},{},{}'.format(
            buff['xmin'], buff['ymin'], buff['xmax'], buff['ymax']
        ),
        'geometryType': 'esriGeometryEnvelope',
        'inSR': sr,
        'spatialRel': 'esriSpatialRelIntersects',
        #'objectIds': None,
        #'where': None,
        #'time': None,
        #'returnCountOnly': False,
        #'returnIdsOnly': False,
        'returnGeometry': True,
        #'maxAllowableOffset': None,
        #'outSR': None,
        'outFields': 'name,stationtriplet',
        'f': 'json',
    }


def query_AWDB(layer_url, query_params):
    # need to get the query url + params
    # then parse the output to build features and return
    print query_params
    resp = requests.get(layer_url, params=query_params)
    return resp.json()
