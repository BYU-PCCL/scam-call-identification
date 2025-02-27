#FROM python:3.11
FROM continuumio/miniconda3

# Install base utilities
RUN apt-get update --allow-unauthenticated\
    && apt-get install -y build-essential \
    && apt-get install -y wget \
    && apt-get install -y git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

#create conda environment
RUN conda create --name scams_env \
    python=3.11

# Set up shell to use bash and activate the environment
SHELL ["/bin/bash", "--login", "-c"]
RUN echo "conda activate scams_env" >> ~/.bashrc

#install dependencies
RUN pip install scikit-learn \
    && pip install pandas \
    && pip install numpy

#other
SHELL ["/bin/bash", "-c"]

RUN echo "alias ls='ls --color=auto'" >> ~/.bashrc

CMD ["bash"]