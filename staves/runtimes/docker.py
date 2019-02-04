import subprocess
from pathlib import Path
from typing import MutableSequence

import docker
from docker.types import Mount


def init(version: str, stage3: str, portage_snapshot: str, libc: str) -> str:
    image_name = f'staves/bootstrap-x86_64-{libc}:{version}'
    command = ['docker', 'build', '--tag', image_name, '--no-cache',
               '-f', f'Dockerfile.x86_64-{libc}', '--build-arg', f'STAGE3={stage3}',
               '--build-arg', f'PORTAGE_SNAPSHOT={portage_snapshot}', '.']
    subprocess.run(command)
    return image_name


def run(builder: str, args: MutableSequence[str], build_cache: str, config: Path, ssh: bool=False, netrc: bool=False):
    docker_client = docker.from_env()
    args.insert(-1, '--config')
    args.insert(-1, '/staves.toml')
    mounts = [
        Mount(type='volume', source=build_cache, target='/usr/portage/packages',),
        Mount(type='bind', source='/run/docker.sock', target='/var/run/docker.sock'),
        Mount(type='bind', source=str(config.resolve()), target='/staves.toml', read_only=True)
    ]
    if ssh:
        ssh_dir = str(Path.home().joinpath('.ssh'))
        mounts += [
            Mount(type='bind', source=ssh_dir, target='/root/.ssh', read_only=True),
            Mount(type='bind', source=ssh_dir, target='/var/tmp/portage/.ssh', read_only=True)
        ]
    if netrc:
        netrc_path = str(Path.home().joinpath('.ssh'))
        mounts += [
            Mount(type='bind', source=netrc_path, target='/root/.netrc', read_only=True),
            Mount(type='bind', source=netrc_path, target='/var/tmp/portage/.netrc', read_only=True)
        ]
    container = docker_client.containers.run(builder, command=args, auto_remove=True, mounts=mounts, detach=True)
    for line in container.logs(stream=True):
        print(line.decode(), end='')
