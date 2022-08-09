#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
mkdir -p ../../toolbar/
rm ../../toolbar/fda.shelf
ln -s $DIR/fda.shelf $DIR/../../toolbar/
