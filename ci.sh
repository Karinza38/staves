#!/usr/bin/env bash
set -e

setup_test_env() {
    echo "Setting up test environment…"
    python3.6 -m venv venv
    . venv/bin/activate
    pip install pip-tools
    pip-sync requirements.txt dev-requirements.txt
}

run_unit_tests() {
    PYTHONPATH=. pytest
}

create_stage3_image() {
    local build_date="$1"
    stage3_filename=stage3-amd64-musl-hardened-${build_date}.tar.bz2
    stage3_path=/tmp/${stage3_filename}
    if [ ! -f ${stage3_path} ]; then
        wget -O ${stage3_path} http://distfiles.gentoo.org/experimental/amd64/musl/${stage3_filename}
    fi
    mkdir gentoo
    fakeroot tar xpjf ${stage3_path} -C gentoo
    docker build --tag staves/gentoo-stage3-amd64-musl-hardened:${build_date} --tag staves/gentoo-stage3-amd64-musl-hardened:latest -f Dockerfile.stage3 .
}

project_name=$(basename $(pwd))
version=$(git describe --tags --always --dirty)
version=${version#${project_name}-}
setup_test_env
run_unit_tests

musl_stage3_date="20180204"
create_stage3_image ${musl_stage3_date}
docker build --tag "staves/builder-musl:${version}.${musl_stage3_date}" --tag "staves/builder-musl:${version}" \
    --tag "staves/builder-musl:${version%.*}" --tag "staves/builder-musl:${version%%.*}" \
    -f Dockerfile.builder-musl .
glibc_stage3_date="20180228"
docker build --tag "staves/builder-glibc:${version}.${glibc_stage3_date}" --tag "staves/builder-glibc:${version}" \
    --tag "staves/builder-glibc:${version%.*}" --tag "staves/builder-glibc:${version%%.*}" \
    -f Dockerfile.builder-glibc .
