import os

# TODO: Rename this file to "files manager"

def list_files():
    """List all downloaded files. Used primarily for debugging purposes.

    Returns:
        A list of file names.
    """
    # Logging
    print 'Listing all downloaded files'

    path = os.path.join(os.getcwd(), 'temp')
    return [f for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))]

def clear_files():
    """Deletes all downloaded files.
    """
    print 'Deleting all downloaded files'

    path = os.path.join(os.getcwd(), 'temp')
    for f in os.listdir(path):
        file_path = os.path.join(path, f)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print e
