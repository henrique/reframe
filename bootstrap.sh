#!/bin/bash
#
# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

#
# Bootstrap script for running ReFrame from source
#

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

CMD()
{
    echo -e "${BLUE}==>${NC}" ${YELLOW}$*${NC} && $*
}

usage()
{
    echo "Usage: $0 [-h] [+docs]"
    echo "Bootstrap ReFrame by pulling all its dependencies"
    echo "  -P EXEC  Use EXEC as Python interpreter"
    echo "  -h       Print this help message and exit"
    echo "  +docs    Build also the documentation"
}


while getopts "hP:" opt; do
    case $opt in
        "P") python=$OPTARG ;;
        "h") usage && exit 0 ;;
        "?") usage && exit 0 ;;
    esac
done

shift $((OPTIND - 1))
if [ -z $python ]; then
    python=python3
fi

pyver=$($python -V | sed -n 's/Python \([0-9]\+\)\.\([0-9]\+\)\..*/\1.\2/p')

# Install pip for Python 3
CMD $python -m ensurepip --root external/ --default-pip

# ensurepip installs pip in `external/usr/` whereas the --target option installs
# everything under `external/`. That's why include both in the PYTHONPATH

export PATH=$(pwd)/external/usr/bin:$PATH
export PYTHONPATH=$(pwd)/external:$(pwd)/external/usr/lib/python$pyver/site-packages:$PYTHONPATH

CMD $python -m pip install -q --upgrade pip --target=external/
CMD $python -m pip install -q -r requirements.txt --target=external/ --upgrade

if [ x"$1" == x"+docs" ]; then
    CMD $python -m pip install -q -r docs/requirements.txt --target=external/ --upgrade
    make -C docs
fi
