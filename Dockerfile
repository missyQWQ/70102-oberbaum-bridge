FROM ubuntu:jammy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3-pip
# uncomment for test
# COPY /src/simulator.py /simulator/
# WORKDIR /simulator
COPY /src/messages.mllp /data/
EXPOSE 8440
EXPOSE 8441
COPY /src/data_loader.py /model/
COPY /src/data_processing.py /model/
COPY /src/main.py /model/
COPY /src/model_feature_construction.py /model/
COPY /src/pager.py /model/
COPY /src/run_model.py /model/
COPY /src/aki.csv /model/
COPY /src/history.csv /model/
COPY /src/dummy_input.csv /model/
COPY requirements.txt /model/
COPY README.md /model/
COPY /src/aki_encoder_model.pkl /model/
COPY /src/clf_model.pkl /model/
COPY /src/sex_encoder_model.pkl /model/
COPY /tests/test_data_processing.py /model/
COPY /tests/test_feature_construction.py /model/
COPY /tests/test_pager.py /model/
RUN pip3 install -r /model/requirements.txt
WORKDIR /model/
RUN echo "$(ls -la )"
RUN pytest
RUN chmod +x /model/main.py
# uncomment for test
# CMD python3 /simulator/simulator.py --messages=/data/messages.mllp
CMD python3 /model/main.py --MLLP_ADDRESS=$MLLP_ADDRESS --PAGER_ADDRESS=$PAGER_ADDRESS
