FROM ubuntu:20.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y python3 python3-pip python-is-python3 git cmake curl

WORKDIR /rhodium_swmm
COPY . .
RUN ./install_rhodium_swmm.sh

RUN pip install pyswmm

WORKDIR /localmnt
