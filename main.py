import os
import json
import threading
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import send_from_directory
from flask import request
from werkzeug.contrib.cache import FileSystemCache

app = Flask(__name__)
cache = FileSystemCache(os.path.join(os.getcwd(), 'cache'))

from youtube import handler
from youtube import validator
from youtube.exceptions import YoutubeError

@app.route('/')
def index():
    return render_template('index.html')

def _get_cache_key(url, filetype):
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

def download_video(url, filetype):
    """Downloads and converts the video

    Args:
        url: A string containing the URL of the video, in any format.
        filetype: A string containing the filetype of the output, as either
        'audio' or 'video'
    """
    cache_key = _get_cache_key(url, filetype)
    # If there's a non-bug error, report it
    try:
        output = handler.initate_download(url, filetype)
        # Give this cache a longer timeout, because it won't change anymore.
        # We still want the result to be cached though, so we don't have to
        # re-download. The other messages we don't want a longer timeout,
        # because we want to be able to retry errors in a reasonable amount
        # of time.
        cache.set(
            cache_key,
            {'status': 'FINISHED', 'data': output},
            timeout=5*60,
        )
    except YoutubeError as e:
        cache.set(
            cache_key,
            {'status': 'ERROR', 'code': 400, 'message': e.message},
            timeout=60,
        )
    except Exception:
        cache.set(
            cache_key,
            {'status': 'ERROR', 'code': 500, 'message': 'Internal Error'},
            timeout=60,
        )


@app.route('/api/download', methods=['POST'])
def download():
    data = request.form
    url = data.get('url')
    filetype = data.get('filetype')

    cache_key = _get_cache_key(url, filetype)

    result = cache.get(cache_key)
    # Download not yet started
    if result is None:
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
            target=download_video,
            args=(url, data.get('filetype'))
        )
        thread.daemon = True
        thread.start()

        # Long timeout, if download exceeds this timeout, I don't care anymore.
        cache.set(cache_key, {'status': 'STARTED'}, timeout=600*60)
        return jsonify(status='STARTING')
    elif result['status'] == 'STARTED':
        return jsonify(status='STARTED')
    elif result['status'] == 'FINISHED':
        return jsonify(status='FINISHED', **result['data'])
    else:
        return jsonify(status='ERROR', message=result['message']), result['code']

@app.route('/api/file')
def get_file():
    filename = request.args.get('filename', None)
    name = request.args.get('name', None)
    if filename is None:
        return ''
    if name:
        name = name.encode("utf-8")
    path = os.path.join(os.getcwd(), 'temp')

    # Logging
    print "Retrieving file:", path, filename, "of name:", name

    return send_from_directory(path, filename, as_attachment=True,
                               attachment_filename=name)

@app.route('/api/all_files')
def list_files():
    # Logging
    print "Listing all downloaded files."

    path = os.path.join(os.getcwd(), 'temp')
    files = [f for f in os.listdir(path)
             if os.path.isfile(os.path.join(path, f))]

    # If there are no files, you still need to return something, or else Heroku
    # returns a 500 error.
    if not files:
        return "There are no files."

    return "\n".join(files)

if __name__ == '__main__':
    app.run(debug=True)
