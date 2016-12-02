import os
import json
import threading
import urllib
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import send_from_directory
from flask import request

app = Flask(__name__)

from backend import list_files
from backend import status_holder

import download_request

from youtube import handler
from youtube import validator
from youtube.exceptions import YoutubeError

# Pages

@app.route('/')
def index():
    """The main download form."""
    return render_template('index.html')


@app.route('/quick')
def quick():
    """An endpoint for Chrome autocomplete, displays the same page, but can
    trigger Javascript that automatically queues up the download.
    """
    return render_template('index.html')

def _download_video(download):
    """Downloads and converts the video.

    Args:
        download: A DownloadRequest object.
    """
    # If there's a non-bug error, report it
    try:
        output = handler.initate_download(download)
        if not os.path.isfile(os.path.join(os.getcwd(), 'temp',
                                           output['filename'])):
            print "Downloaded file missing. Retrying and forcing mp4 filetype."
            download.set_force_mp4_filetype(True)
            output = handler.initate_download(download)

        status_holder.set_finished(download, output)
    except YoutubeError as e:
        status_holder.set_error(download, e.message, 400)
    except Exception:
        status_holder.set_error(download, 'Internal Error', 500)

# APIs

@app.route('/api/download', methods=['POST'])
def download():
    """Accepts the download request.

    Doesn't directly download the video, but instead queues up a thread to
    download the video. This is so that we can return some result immediately,
    to satisfy Heroku's policy of returning requests within 30 seconds.

    Args: (Passed in through the form)
        url: A string containing the URL of the video, in any format.
        filetype: A string containing the filetype of the output, as either
        'audio' or 'video'

    Returns:
        JSON containing the progress of the download.
    """
    data = request.form

    try:
        download = download_request.DownloadRequest(
                data.get('url'), data.get('filetype'))
    except YoutubeError as e:
        return jsonify(status='ERROR', message=e.message), 400

    if data.get('enable_trim') == "on":
        try:
            download.set_time_trimming(data.get("start_time"), data.get("end_time"))
        except YoutubeError as e:
            return jsonify(status='ERROR', message=e.message), 400

    cached_data = status_holder.get_entry(download)
    # Download not yet started
    if cached_data is None:
        # Download the video in another thread.
        # We use another thread so that we can return some result immediately,
        # in order to satisfy Heroku's "must return something" policy.
        thread = threading.Thread(
            target=_download_video,
            args=(download,),
        )
        thread.daemon = True
        thread.start()

        # Long timeout, if download exceeds this timeout, I don't care anymore.
        status_holder.set_downloading(download)
        return jsonify(status='STARTING')
    elif cached_data['status'] == status_holder.DOWNLOADING_STATUS:
        # TODO: Change to "starting". Or change the other thing to "started".
        return jsonify(status='STARTED')
    elif cached_data['status'] == status_holder.FINISHED_STATUS:
        # We need to URL encode the key so it can be passed as a query parameter
        encoded_key = urllib.quote(status_holder.get_cache_key(download))
        return jsonify(status='FINISHED', key=encoded_key,
                       **cached_data['data'])
    elif cached_data['status'] == status_holder.ERROR_STATUS:
        result = jsonify(status='ERROR', message=cached_data['message'])
        return result, cached_data['code']

    assert False


@app.route('/api/file')
def get_file():
    """Gets the downloaded and processed file.

    We use the cache_key in order to keep track of the file's information.

    Args: (Passed in through request.args)
        key: The cache key of the specified video.

    Returns:
        The specified file over HTTP.
    """
    cache_key = request.args.get('key', None)
    print "Getting information for cache key:", cache_key
    if not cache_key:
        return '', 400

    cached_data = status_holder.get_entry_from_key(cache_key)
    if not cached_data:
        return 'File not found. Please try again.', 400
    filename = cached_data['data']['filename']
    # We need to be able to handle unicode characters
    name = cached_data['data']['title'].encode('utf-8')

    path = os.path.join(os.getcwd(), 'temp')

    # Logging
    print "Retrieving file:", path, filename, "of name:", name

    return send_from_directory(path, filename, as_attachment=True,
                               attachment_filename=name)


@app.route('/api/all_files')
def list_files_route():
    """Lists all files. Used for primarily debugging reasons.

    Files are delimited by newline characters.
    """
    files = list_files.list_files()

    # If there are no files, you still need to return something, or else Heroku
    # returns a 500 error.
    if not files:
        return 'There are no files.'

    return '\n'.join(files)


if __name__ == '__main__':
    app.run(debug=True)
