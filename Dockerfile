FROM bistromath/gnuradio:v3.9

ENV num_threads 10
MAINTAINER bistromath@gmail.com version: 0.1

WORKDIR /opt

RUN apt install -y python3-zmq python3-scipy

RUN mkdir gr-air_modes
COPY . gr-air_modes/
WORKDIR /opt/gr-air_modes
RUN mkdir build && cd build && cmake ../ && make -j${num_threads} && make install && ldconfig
