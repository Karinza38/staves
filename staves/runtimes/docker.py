from typing import IO, Sequence

import subprocess


def run(builder: str, args: Sequence[str], build_cache: str, config_file: IO, ssh: bool=False, netrc: bool=False):
    command = [
        'docker', 'run', '--rm', '--interactive',
        '--mount', f'type=volume,source={build_cache},target=/usr/portage/packages',
        '--mount', 'type=bind,source=/run/docker.sock,target=/var/run/docker.sock'
    ]
    if ssh:
        command += [
            '--mount', 'type=bind,source=${HOME}/.ssh,target=/root/.ssh,readonly',
            '--mount', 'type=bind,source=${HOME}/.ssh,target=/var/tmp/portage/.ssh,readonly'
        ]
    if netrc:
        command += [
            '--mount', 'type=bind,source=${HOME}/.netrc,target=/root/.netrc,readonly',
            '--mount', 'type=bind,source=${HOME}/.netrc,target=/var/tmp/portage/.netrc,readonly'
        ]
    command += [builder, *args]
    subprocess.run(command , stdin=config_file)