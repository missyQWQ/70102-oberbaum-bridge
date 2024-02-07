FROM ubuntu:jammy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3-pip
COPY simulator.py /simulator/
COPY simulator_test.py /simulator/
WORKDIR /simulator
RUN ./simulator_test.py
COPY messages.mllp /data/
EXPOSE 8440
EXPOSE 8441
# COPY __init__.py /model/
COPY data_loader.py /model/
COPY data_processing.py /model/
COPY main.py /model/
COPY model_feature_construction.py /model/
COPY pager.py /model/
COPY run_model.py /model/
COPY aki.csv /model/
COPY history.csv /model/
COPY dummy_input.csv /model/
# COPY pytest.ini /model/
COPY requirements.txt /model/
COPY README.md /model/
COPY aki_encoder_model.pkl /model/
COPY clf_model.pkl /model/
COPY sex_encoder_model.pkl /model/
COPY tests /model/tests/
RUN pip3 install -r /model/requirements.txt
WORKDIR /model/
RUN echo "$(ls -la )"
# RUN pytest
CMD /simulator/simulator.py --messages=/data/messages.mllp
# CMD python3 /model/main.py --MLLP_ADDRESS=$MLLP_ADDRESS --PAGER_ADDRESS=$PAGER_ADDRESS
