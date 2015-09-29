def get_cache_key(url, filetype):
    """Gets the key for the cache based on its url and filetype

    No guarantees are made about the content of the url, and two different
    urls pointing to the same video will return different keys.

    Args:
        url: A string containing the URL of the video, in any format.
        filetype: A string containing the filetype of the output, as either
        'audio' or 'video'

    Returns:
        A should-be unique string useful for being the key of a hashtable for
        that video and filetype.
    """
    return url + '::::' + filetype
