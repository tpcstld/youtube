"""Contains data about a download request.
"""

class DownloadRequest(object):

    def __init__(self, url, filetype):
        """Constructs a DownloadRequest

        Args:
            url: A string containing the URL of the video, in any format.
            filetype: A string containing the filetype of the output, as either
            'audio' or 'video'
        """
        # Users might not include a protocol, we need to add it.
        if not '//' in url:
            url = '//' + url

        self.url = url
        self.filetype = filetype

    def get_url(self):
        return self.url

    def get_filetype(self):
        return self.filetype

    # TODO: Time constraints.
