#!/usr/bin/bash
apt-get install sysv-rc-softioc
if [ ! -d /opt/conda_envs/services/ ]; then conda create -p /opt/conda_envs/services python=3.5; fi
source activate services
conda install pymongo ujson tornado jsonschema yaml pytz doct
pip install requests
mkdir /services
cd /services
mkdir -p /epics/iocs/

t clone https://github.com/NSLS-II/amostra.git
cd amostra
python setup.py develop

mkdir -p /epics/iocs/amostra/
cd /epics/iocs/amostra

echo "NAME=amostra
PORT=$(manage-iocs nextport)
HOST=$HOSTNAME
USER=tornado" > config

echo '#!/bin/bash
export PATH=/opt/conda/bin:$PATH
source activate services
python /services/amostra/startup.py --mongo-host=localhost --mongo-port=27017 --database=amostra --service-port=7770 --timezone=US/Eastern' > launch.sh


ln -s -T launch.sh st.cmd

chown -R tornado:tornado /epics/iocs/amostra

manage-iocs install amostra
manage-iocs enable amostra
/etc/init.d/softioc-amostra start

