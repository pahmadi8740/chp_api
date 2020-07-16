# first stage of build to pull repos
FROM ubuntu as intermediate

# install git
RUN apt-get update \
	&& apt-get install -y git

# add credentials on build
ARG SSH_PRIVATE_KEY
ARG SSH_PUBLIC_KEY
RUN mkdir -p /root/.ssh/ \
	&& chmod 0700 /root/.ssh \
	&& ssh-keyscan intuition.thayer.dartmouth.edu >> ~/.ssh/known_hosts \
	&& chmod 644 ~/.ssh/known_hosts

# add keys (use in windows powershell)
COPY ./id_rsa /root/.ssh/
COPY ./id_rsa.pub /root/.ssh/
RUN chmod 600 /root/.ssh/id_rsa \
	&& chmod 600 /root/.ssh/id_rsa.pub

# add keys (use in Linux)
#RUN echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa \
#	&& echo "${SSH_PUBLIC_KEY}" > /root/.ssh/id_rsa.pub \
#	&& chmod 600 /root/.ssh/id_rsa \
#	&& chmod 600 /root/.ssh/id_rsa.pub

#RUN ssh cyakaboski@intuition.thayer.dartmouth.edu -t -t -v -o StrictHostKeyChecking=no

RUN git clone ssh://cyakaboski@intuition.thayer.dartmouth.edu/home/public/git/modules/PyBKB.git
RUN git clone ssh://cyakaboski@intuition.thayer.dartmouth.edu/home/public/git/projects/ChpData.git
RUN git clone https://github.com/di2ag/bkb-pathway-provider.git

#pull official base image
FROM ubuntu:20.04

# copy repo to new image
COPY --from=intermediate /PyBKB /srv/PyBKB
COPY --from=intermediate /ChpData /srv/ChpData
COPY --from=intermediate /bkb-pathway-provider /srv/bkb-pathway-provider

# set work directory
WORKDIR /usr/src/chp_api

# set ARGs
ARG DEBIAN_FRONTEND=noninterative

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=America/New_York

# install dependencies
RUN apt-get update \
	&& apt-get install -y python3-pip graphviz openmpi-bin libopenmpi-dev build-essential libssl-dev libffi-dev python3-dev 

RUN apt-get install -y libgraphviz-dev python3-pygraphviz
RUN apt-get install -y libpq-dev
RUN apt-get install -y netcat

# install django dependencies
RUN pip3 install --upgrade pip

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install wheel

# install pybkb
RUN cd /srv/PyBKB && python3 setup.py bdist_wheel && cd dist && pip3 install pybkb-1.0.0-py3-none-any.whl

# install chp
RUN cd /srv/bkb-pathway-provider && python3 setup.py bdist_wheel && cd dist && pip3 install chp-1.0.0-py3-none-any.whl

# install chp-data
RUN cd /srv/ChpData && python3 setup.py bdist_wheel && cd dist && pip3 install chp_data-0.0.1-py3-none-any.whl

RUN pip3 freeze

# copy entry point
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/chp_api/entrypoint.sh"]
