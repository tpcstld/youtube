"""Holds the current status of downloads.

Heroku enforces that requests must return within a certain amount of time.
This restriction, around 60 seconds currently, is too short for some videos to
download correctly. In order to get around this, we do the downloading and
processing asynchronously, while holding the current state and progress.
"""
# TODO: Tests

import enum

from werkzeug.contrib.cache import FileSystemCache

# For a single dyno, there can be more than one serving instances.We leverage
# the shared emphemial filesystem as the cache.
cache = FileSystemCache(os.path.join(os.getcwd(), 'cache'))

# The duration, in seconds, that a particular cache entry will be stored for.
NORMAL_CACHE_SECONDS = 3600
ERROR_CACHE_SECONDS = 60

# The various statuses of a download.Used by the front - end to show the state
# of the download.
@enum.unique
class Status(enum.Enum):
    FINISHED = 1
    ERROR = 2
    DOWNLOADING = 3

    def __str__(self):
        if self == self.FINISHED:
            return "FINISHED"
        elif self == self.ERROR:
            return "ERROR"
        elif self == self.DOWNLOADING:
            # TODO: Change this constant to DOWNLOADING.Then we can just use
            # self.name
            return "STARTED"

        # This code should never be run.
        assert False

def _get_cache_key(url, filetype):
    """Gets the key for querying the status based on its url and filetype

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

# TODO: Remove this function.
def get_cache_key(url, filetype):
    """Temporary function for compatibility.
    """
    return _get_cache_key(url, filetype)

def set_downloading(url, filetype):
    """Sets the status of the download to "downloading".

    Args:
        url: A string containing the URL of the video, in any format.
        filetype: A string containing the filetype of the output, as either
        'audio' or 'video'
    """
    cache.set(
        _get_cache_key(url, filetype),
        {'status': Status.DOWNLOADING},
        timeout=NORMAL_CACHE_SECONDS,
    )

# TODO: Specify the data as a namedtuple.
def set_finished(url, filetype, data):
    """Sets the status of the download to "finished".

    Args:
        url: A string containing the URL of the video, in any format.
        filetype: A string containing the filetype of the output, as either
        'audio' or 'video'
        data: Extra data about the download.
    """
    cache.set(
        _get_cache_key(url, filetype),
        {'status': Status.DOWNLOADING, 'data': data},
        timeout=NORMAL_CACHE_SECONDS,
    )

def set_error(url, filetype, message, code):
    """Sets the status of the download to "errored".

    Args:
        url: A string containing the URL of the video, in any format.
        filetype: A string containing the filetype of the output, as either
        'audio' or 'video'
        message: The error message.
        code: The HTTP status code to return.
    """
    cache.set(
        _get_cache_key(url, filetype),
        {'status': Status.ERROR, 'code': code, 'message': message},
        timeout=ERROR_CACHE_SECONDS,
    )

# TODO: Remove this.
def get_entry(url, filetype):
    """Temporary function for backwards compatibility.
    """
    return cache.get(_get_cache_key(url, filetype))

# TODO: Remove this.
def get_entry_from_key(cache_key):
    """Temporary function for backwards compatibility.
    """
    return cache.get(cache_key)

def get_status(url, filetype):
    """Returns the status of the download.

    Args:
        url: A string containing the URL of the video, in any format.
        filetype: A string containing the filetype of the output, as either
        'audio' or 'video'
    """
    data = cache.get(_get_cache_key(url, filetype))
    if data is None:
        return None
    return data['status']

def get_finished_data(url, filetype):
    """Returns the extra data about a finished download.

    Args:
        url: A string containing the URL of the video, in any format.
        filetype: A string containing the filetype of the output, as either
        'audio' or 'video'
    """
    # TODO: Verify that the download is finished.
    return cache.get(_get_cache_key(url, filetype))['data']
