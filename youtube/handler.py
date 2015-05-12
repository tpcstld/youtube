import os

import constants
import downloader
import convertor

def initate_download(url, filetype):
    """Validates, downloads and possibly converts the video, depending on filetype
    """
    try:
        file_path, title = downloader.download(url)
    except:
        return False, 'Error processing file or url'

    file_ext = os.path.splitext(file_path)[1]

    # Convert the video if the selected file type is 'audio'
    if filetype == constants.AUDIO_FILETYPE_NAME:
        print 'htht'
        try:
            original_file_path = os.path.splitext(file_path)[0]  # No extension
            file_ext = '.mp3'
            new_file_path = original_file_path + '.mp3'
            print file_path, new_file_path
            print convertor.convert(file_path, new_file_path)
        except:
            return False, 'Error converting video to audio'

    filename = os.path.splitext(os.path.basename(file_path))[0] + file_ext

    output = {
        'filename': filename.encode('ascii', 'xmlcharrefreplace'),
        'title': title.encode('ascii', 'xmlcharrefreplace') + file_ext.encode('ascii', 'xmlcharrefreplace'),
    }

    return True, output
