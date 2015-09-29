import subprocess
import os

def _find_matching_file(filename):
    """Finds a matching filename, defaults to the original filename
    if it exists. If it doesn't exist, try to find a file with the same
    name but different extension

    Args:
        filename(str): The filename to match includes name and extension

    Returns:
        string representing the file to convert.
        Empty string ("") if no file can be found.
            (This is so that os.path.isfile doesn't break)

    Notes:
        This is because YoutubeDL seems to give the wrong file extension
        of the downloaded file sometimes.
    """
    # We want the chosen filename to have the first priority
    if os.path.isfile(filename):
        return filename

    # Match same filename, different extension
    name, _ = os.path.splitext(filename)
    path = os.path.join(os.getcwd(), 'temp')
    files = [f for f in os.listdir(path)
             if os.path.isfile(os.path.join(path, f))]
    print "Found all files:", " ".join(files)
    files = [f for f in files if f.startswith(os.path.basename(name))]

    if len(files) > 0:
        new_filename = os.path.join(path, files[0])
        print "Converting", new_filename, "instead of", filename
        return new_filename
    else:
        print "Cannot find matching filename for", filename
        return ""

def convert(source, target):
    """Converts the file from 'source' to 'target' using FFMPEG

    Args:
        source(str): Filepath to the source file
        target(str): Filepath to the target file

    Returns:
        The process that is converting the file.
    """
    print 'Converting file:', source, 'to', target

    # Find any matching file
    source = _find_matching_file(source)

    if not os.path.isfile(source):
        print 'Not converting because source file is missing'
        return

    if os.path.isfile(target):
        print 'Not converting because target file exists'
        return

    command = 'ffmpeg -y -i {source} -f wav - | lame - {target}'.format(
        source=source,
        target=target,
    )

    print 'Running command:', command
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True,
    )

    # Blocking call
    process.wait()

    # Save some disk space
    if source != target:
        os.remove(source)

    return process.communicate()
