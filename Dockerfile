FROM ubuntu:jammy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3
COPY simulator.py /simulator/
COPY simulator_test.py /simulator/
WORKDIR /simulator
RUN ./simulator_test.py
COPY messages.mllp /data/
EXPOSE 8440
EXPOSE 8441
CMD /simulator/simulator.py --messages=/data/messages.mllp