#!/bin/bash
cd /home/simon/projects/ApolloFix/apollofix
mkdir temp
export PYTHONPATH=./temp
/usr/bin/python setup.py build develop --install-dir ./temp
cp ./temp/ApolloFix.egg-link /home/simon/.config/deluge/plugins
rm -fr ./temp
