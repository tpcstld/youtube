def get_download_url(text):
    url = text.split(' ')[-1]
    if not '//' in url:
        url = '//' + url

    return url
