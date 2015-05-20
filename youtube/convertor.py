import subprocess
import os

def convert(source, target):
    """Converts the file from 'source' to 'target' using FFMPEG

    Args:
        source(str): Filepath to the source file
        target(str): Filepath to the target file

    Returns:
        The process that is converting the file.
    """
    if not os.path.isfile(source):
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
    if source != target:
        os.remove(source)
    return process.communicate()
