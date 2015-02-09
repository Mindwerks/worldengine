#!/bin/sh

x=${1:-"150"}
y=${2:-"150"}
name=${3:-"myworld"}

#pybin="python"
pybin="python2.7"

export PYTHONPATH=.:..
time $pybin lands/generator.py -x $x -y $y -s 1 -n $name
#time $pybin lands/generator.py ancient_map -w $name.world

