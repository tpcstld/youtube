import os
import json
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import send_from_directory
from flask import request

app = Flask(__name__)

from youtube import handler
from youtube.exceptions import YoutubeError

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def download():
    data = request.form

    # If there's a non-bug error, report it
    try:
        output = handler.initate_download(data.get('url'), data.get('filetype'))
    except YoutubeError as e:
        return jsonify(message=e.message), 400

    return jsonify(**output)

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
