class YoutubeError(Exception):
    """Generic exception class for everything
    """
    pass

class ValidationError(YoutubeError):
    """Exception class for validation errors
    """
    pass

class DownloadError(YoutubeError):
    """Exception class for downloading errors
    """
    pass
