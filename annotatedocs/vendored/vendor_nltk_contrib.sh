#!/bin/bash

pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

cd $SCRIPTPATH

curl -s -L https://github.com/nltk/nltk_contrib/tarball/master | \
    tar --strip-components=1 --wildcards -zxvf - "*/nltk_contrib"
