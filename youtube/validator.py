import urlparse

import constants
from exceptions import ValidationError

def _is_url_from_youtube(url):
    """Checks whether or not an URL is from youtube

    Args:
        url(str): The URL string to check

    Returns:
        True if the URL is a youtube url, otherwise False.
    """
    location = urlparse.urlparse(url).netloc
    # Two possible youtu.be is the shortlink version of youtube
    return 'youtube.' in location or 'youtu.be' in location

def _is_playlist_url(url):
    """Checks whether or not the URL is for a youtube playlist
    A url that is about both a youtube playlist and video will return False.

    Args:
        url(str): The URL string to check

    Returns:
        True if the URL is for only a youtube playlist, otherwise False.
    """
    query = urlparse.parse_qs(urlparse.urlparse(url).query)
    return 'list' in query and 'v' not in query

def validate_url(url):
    """Validates the url.

    Args:
        url(str): The URL to validate

    Raises:
        ValidationError: If the validation has failed
    """
    # We don't allow downloading from other sites except for youtube
    if not _is_url_from_youtube(url):
        raise ValidationError('Invalid URL')

    # We don't allow downloading playlists
    if _is_playlist_url(url):
        raise ValidationError('Playlist downloading in not supported')

def validate_filetype(filetype):
    """Validates that the filetype is appropriate.

    Args:
        filetype(str): The filetype to validate.

    Raises:
        ValidationError: If the validation has failed.
    """
    if filetype != constants.AUDIO_FILETYPE_NAME and filetype != constants.VIDEO_FILETYPE_NAME:
        raise ValidationError("Invalid filetype.")
