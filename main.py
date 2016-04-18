import os
import json
import threading
import urllib
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import send_from_directory
from flask import request
from werkzeug.contrib.cache import FileSystemCache

app = Flask(__name__)

# We use a file cache in order to remain consistent across all serving instances
cache = FileSystemCache(os.path.join(os.getcwd(), 'cache'))

from backend import list_files
from backend import get_cache_key

from youtube import handler
from youtube import validator
from youtube.exceptions import YoutubeError

# Constants

# How long do we want to store a successful download, in seconds.
OK_CACHE_SECONDS = 60 * 60  # One hour.
# How long do we want to store a failed download, in seconds.
BAD_CACHE_SECONDS = 60  # One minute.

# Pages

@app.route('/')
def index():
    """The main download form."""
    return render_template('index.html')


@app.route('/watch')
def watch():
    """The same main download form, but can trigger javascript that
    automatically queues up the video download.
    """
    return render_template('index.html')


def _download_video(url, filetype):
    """Downloads and converts the video.

    Args:
        url: A string containing the URL of the video, in any format.
        filetype: A string containing the filetype of the output, as either
        'audio' or 'video'
    """
    cache_key = get_cache_key.get_cache_key(url, filetype)
    # If there's a non-bug error, report it
    try:
        output = handler.initate_download(url, filetype, False)
        if not os.path.isfile(os.path.join(os.getcwd(), 'temp',
                                           output['filename'])):
            print "Downloaded file missing. Retrying and forcing mp4 filetype."
            output = handler.initate_download(url, filetype, True)

        # Give this cache a longer timeout, because it won't change anymore.
        # We still want the result to be cached though, so we don't have to
        # re-download. The other messages we don't want a longer timeout,
        # because we want to be able to retry errors in a reasonable amount
        # of time.
        cache.set(
            cache_key,
            {'status': 'FINISHED', 'data': output},
            timeout=OK_CACHE_SECONDS,
        )
    except YoutubeError as e:
        cache.set(
            cache_key,
            {'status': 'ERROR', 'code': 400, 'message': e.message},
            timeout=BAD_CACHE_SECONDS,
        )
    except Exception:
        cache.set(
            cache_key,
            {'status': 'ERROR', 'code': 500, 'message': 'Internal Error'},
            timeout=BAD_CACHE_SECONDS,
        )

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
    url = data.get('url')
    filetype = data.get('filetype')

    # Users might not include a protocol
    if not '//' in url:
        url = '//' + url

    cache_key = get_cache_key.get_cache_key(url, filetype)

    cached_data = cache.get(cache_key)
    # Download not yet started
    if cached_data is None:
        # Do a preemptive validation screen, so we don't waste time processing
        # videos that are going to error out anyways.
        try:
            validator.validate_url(url)
        except YoutubeError as e:
            return jsonify(status='ERROR', message=e.message), 400

        # Download the video in another thread.
        # We use another thread so that we can return some result immediately,
        # in order to satisfy Heroku's "must return something" policy.
        thread = threading.Thread(
            target=_download_video,
            args=(url, data.get('filetype'))
        )
        thread.daemon = True
        thread.start()

        # Long timeout, if download exceeds this timeout, I don't care anymore.
        cache.set(cache_key, {'status': 'STARTED'}, timeout=600*60)
        return jsonify(status='STARTING')
    elif cached_data['status'] == 'STARTED':
        return jsonify(status='STARTED')
    elif cached_data['status'] == 'FINISHED':
        # We need to URL encode the key so it can be passed as a query parameter
        encoded_key = urllib.quote(cache_key)
        return jsonify(status='FINISHED', key=encoded_key,
                       **cached_data['data'])
    else:
        result = jsonify(status='ERROR', message=cached_data['message'])
        return result, cached_data['code']


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

    cached_data = cache.get(cache_key)
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
