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

def get_cache_key(url, filetype):
    """Gets the key for the cache based on its url and filetype
    """
    return url + '::::' + filetype

def download_video(url, filetype):
    """Downloads and converts the video
    """
    cache_key = get_cache_key(url, filetype)
    # If there's a non-bug error, report it
    try:
        output = handler.initate_download(url, filetype)
        cache.set(
            cache_key,
            {'status': 'FINISHED', 'data': output},
            timeout=5*60, # Give it a longer timeout
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

    cache_key = get_cache_key(url, filetype)

    result = cache.get(cache_key)
    # Download not yet started
    if result is None:
        # Do a preemptive validation screen
        try:
            validator.validate_url(url)
        except YoutubeError as e:
            return jsonify(status='ERROR', message=e.message), 400

        # Download the video in another thread
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

    path = os.path.join(os.getcwd(), 'temp')
    print path, filename
    return send_from_directory(path, filename, as_attachment=True,
                               attachment_filename=name)

if __name__ == '__main__':
    app.run(debug=True)
