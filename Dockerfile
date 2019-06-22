FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update


# -----------------------------------------

RUN pip install --upgrade pip
RUN pip install cobra
RUN pip install escher
RUN pip install networkx
RUN pip install cobrakbase==0.1.9

COPY ./ /kb/module

RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

RUN mkdir -p /root/.cache/escher/1-0-0/5
RUN mv /kb/module/data/escher/maps  /root/.cache/escher/1-0-0/5
RUN mv /kb/module/data/escher/models  /root/.cache/escher/1-0-0/5


ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
