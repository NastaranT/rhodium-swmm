#!/bin/bash

token=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
bitbucket_token=mcHhT9xAAQf60yWKQ4lZ5D4A

pip install wheel




#./setup_swmm.sh

pip install -r requirements.txt
python setup.py develop

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py pip==21.3.1


pip install pyswmm


pushd example
python setup.py develop
popd
