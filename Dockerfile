FROM kochanowski/projektzapisy:base

COPY zapisy/ /vagrant/zapisy/

WORKDIR /vagrant/zapisy

RUN yarn
RUN /bin/bash -c mount --bind /vagrant_node_modules /vagrant/zapisy/node_modules
RUN apt-get -y install python3-pip

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN pip3 install -U pipenv
RUN pipenv run pip install -r requirements.development.txt

ENV PYTHONPATH="$PYTHONPATH:/vagrant/zapisy"

RUN echo "alias python=python3" >> /home/vagrant/.bashrc
RUN echo "alias python=python3" >> /root/.bashrc

RUN export LC_ALL=C.UTF-8
RUN export LANG=C.UTF-8

EXPOSE 8000
CMD [ "pipenv" "run" "python3" "run.py" "server" ]