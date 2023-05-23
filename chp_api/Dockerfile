###########
# BUILDER #
###########

# first stage of build to pull repos
FROM python:3.8 as intermediate

# set work directory
WORKDIR /usr/src/chp_api

RUN git clone --single-branch --branch master https://github.com/di2ag/trapi_model.git
RUN git clone --single-branch --branch master https://github.com/di2ag/chp_utils.git
RUN git clone --single-branch --branch master https://github.com/di2ag/chp_look_up.git
RUN git clone --single-branch --branch master https://github.com/di2ag/gene-specificity.git

# install dependencies
COPY ./requirements.txt .
RUN pip3 wheel --no-cache-dir --no-deps --wheel-dir /usr/src/chp_api/wheels -r requirements.txt

# gather trapi model wheel
RUN cd trapi_model && python3 setup.py bdist_wheel && cd dist && cp trapi_model-*-py3-none-any.whl /usr/src/chp_api/wheels

# gather chp-utils wheel
RUN cd chp_utils && python3 setup.py bdist_wheel && cd dist && cp chp_utils-*-py3-none-any.whl /usr/src/chp_api/wheels

#gather chp_look_up wheel
RUN cd chp_look_up && python3 setup.py bdist_wheel && cd dist && cp chp_look_up-*-py3-none-any.whl /usr/src/chp_api/wheels

#gather gene specificity wheel
RUN cd gene-specificity && python3 setup.py bdist_wheel && cd dist && cp gene_specificity-*-py3-none-any.whl /usr/src/chp_api/wheels

#########
# FINAL #
#########

#pull official base image
FROM python:3.8

# add app user
RUN groupadd chp_api && useradd -ms /bin/bash -g chp_api chp_api

# create the appropriate directories
ENV HOME=/home/chp_api
ENV APP_HOME=/home/chp_api/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=America/New_York

# set ARGs
ARG DEBIAN_FRONTEND=noninterative

# copy repo to new image
COPY --from=intermediate /usr/src/chp_api/wheels /wheels
COPY --from=intermediate /usr/src/chp_api/requirements.txt .
RUN pip3 install --no-cache /wheels/*

# copy project
COPY ./chp_api $APP_HOME/chp_api
COPY ./manage.py $APP_HOME
COPY ./dispatcher $APP_HOME/dispatcher
COPY ./gunicorn.config.py $APP_HOME

# chown all the files to the app user
RUN chown -R chp_api:chp_api $APP_HOME \
    && chmod 700 $APP_HOME/staticfiles

# change to the app user
USER chp_api
