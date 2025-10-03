#!/bin/bash
export MALMO_XSD_PATH=/home/carlos/MalmoPlatform/Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6/Schemas
export LD_LIBRARY_PATH=/home/carlos/MalmoPlatform/Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/home/carlos/MalmoPlatform/Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6/Python_Examples:$PYTHONPATH
source ~/.pyenv/versions/malmo-py36/bin/activate
python "$@"
