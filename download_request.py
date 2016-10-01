"""Contains data about a download request.
"""
from youtube import constants

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
        self.force_mp4_filetype = False

    def get_url(self):
        return self.url

    def get_filetype(self):
        return self.filetype

    def is_audio_only(self):
        return self.get_filetype() == constants.AUDIO_FILETYPE_NAME

    def set_force_mp4_filetype(self, value):
        self.force_mp4_filetype = value

    def get_force_mp4_filetype(self):
        return self.force_mp4_filetype

    # TODO: Time constraints.
