import os

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
