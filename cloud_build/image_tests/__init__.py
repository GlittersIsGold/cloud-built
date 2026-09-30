import contextlib
import os
import shutil
import subprocess
import re
import tempfile

from .lxd import test_lxd
from .docker import test_docker


@contextlib.contextmanager
def pushtmpd():
    previous_dir = os.getcwd()
    tmpdir = tempfile.mkdtemp()
    try:
        os.chdir(tmpdir)
        yield tmpdir
    finally:
        os.chdir(previous_dir)
        shutil.rmtree(tmpdir)


def test(method, image, branch, arch):
    result = True

    #if arch not in ['x86_64', 'i586']:
    #    return True
    
    home_dir = f"{os.path.expanduser('~')}/cloud-build"

    with pushtmpd() as tmpdir:
        image = shutil.copy2(image, tmpdir)
        image_name = os.path.basename(image)
        if method == 'lxd':
            commands = test_lxd(image, branch, arch)
        elif method == 'docker':
            commands = test_docker(image_name, branch, arch)
        elif match := re.match(r'prog\(([-.\w]+)\)', method):
            if arch not in ['x86_64', 'i586']:
                print(f"Can't run test via vml for arch {arch}")
                return True
            commands = [f"{home_dir}/{match[1]} {image} {branch}"]
        else:
            raise Exception(f'Undefined test method {method}')

        for command in commands:
            rc = subprocess.run(command, shell=True, capture_output=True, text=True)
            if rc.returncode:
                result = False
                print(f'ERROR: Command failed with return code {rc.returncode}')
                print(f'  Command: {command}')
                if rc.stderr:
                    print(f'  stderr: {rc.stderr}')
    return result
