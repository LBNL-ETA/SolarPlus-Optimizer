FROM michaelwetter/ubuntu-1604_jmodelica_trunk

ENV ROOT_DIR /usr/local

USER root

# Install MPCPy
# -------------
RUN apt-get update && apt-get install -y \
	libgeos-dev \
	git

USER developer
WORKDIR $HOME

RUN pip install --user \
	pandas==0.20.3 \
	python-dateutil==2.6.1 \
	pytz==2017.2 \
	scikit-learn==0.18.2 \
	sphinx==1.6.3 \
	numpydoc==0.7.0 \
	tzwhere==2.3 \
	influxdb==5.0.0

RUN mkdir git && cd git && \
    mkdir mpcpy && cd mpcpy && git clone https://github.com/lbl-srg/MPCPy && cd .. && \
    mkdir estimationpy-ka && cd estimationpy-ka && git clone https://github.com/krzysztofarendt/EstimationPy-KA && cd .. && \
    mkdir buildings && cd buildings && git clone https://github.com/lbl-srg/modelica-buildings.git

WORKDIR $ROOT_DIR

ENV JMODELICA_HOME $ROOT_DIR/JModelica
ENV IPOPT_HOME $ROOT_DIR/Ipopt-3.12.4
ENV SUNDIALS_HOME $JMODELICA_HOME/ThirdParty/Sundials
ENV SEPARATE_PROCESS_JVM /usr/lib/jvm/java-8-openjdk-amd64/
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
ENV PYTHONPATH $PYTHONPATH:$HOME/git/estimationpy-ka/EstimationPy-KA:$HOME/git/mpcpy/MPCPy:$JMODELICA_HOME/Python:$JMODELICA_HOME/Python/pymodelica
ENV MODELICAPATH $MODELICAPATH:$HOME/git/buildings/modelica-buildings



