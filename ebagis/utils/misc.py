def random_string(length=5):
    """
    Returns a string of random letters (uppercase and lowercase) and numbers of
    length specified by the optional length argument. Defualt string length is
    5.
    """
    import string
    import random
    return ''.join(random.choice(string.ascii_letters +
                                 string.digits) for i in xrange(length))


def make_short_name(name, maxlength=15):
    """
    Take a string (name), replace spaces with _, and return result less than a
    maximum length, defined by the optional maxlength parameter. Defualt is max
    length of 15 characters.
    """
    nospaces = "_".join(name.split())

    length = len(nospaces)
    if length > maxlength:
        length = maxlength

    return nospaces[:length]


def generate_random_name(layershortname, ext=""):
    return layershortname + "_" + random_string() + ext


def get_queryset_arguments(object):
    """This function is used by some of the view functions to
    determine what URL arguments are to be used to filter instance
    queries. For example, finding all layers from a geodatabase in
    a specific AOI, the goedatabase and AOI ids would be used as
    the filters."""
    from ..constants import URL_FILTER_QUERY_ARG_PREFIX

    query_dict = {}
    for kwarg in object.kwargs:
        if kwarg.startswith(URL_FILTER_QUERY_ARG_PREFIX):
            query_lookup = kwarg.replace(
                URL_FILTER_QUERY_ARG_PREFIX,
                '',
                1
            )
            query_value = object.kwargs.get(kwarg)
            query_dict[query_lookup] = query_value
    return query_dict

