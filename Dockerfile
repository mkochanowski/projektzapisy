FROM kochanowski/projektzapisy:base

COPY zapisy/ /vagrant/zapisy/
# RUN mkdir /vagrant/zapisy/.venv

WORKDIR /vagrant/zapisy

RUN yarn
RUN /bin/bash -c mount --bind /vagrant_node_modules /vagrant/zapisy/node_modules
RUN apt-get -y install python3-pip

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# RUN pip3 install -U pipenv
# RUN python3 -m venv /home/vagrant/env3
# RUN ["/bin/bash" "-c" "source" "/home/vagrant/env3/bin/activate" ]
RUN pip3 install -r requirements.development.txt

ENV PYTHONPATH="$PYTHONPATH:/vagrant/zapisy"

RUN echo "alias python=python3" >> /home/vagrant/.bashrc
RUN echo "alias python=python3" >> /root/.bashrc

RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /vagrant/zapisy
RUN mkdir -p /vagrant/zapisy/logs

EXPOSE 8000
CMD [ "python3" "run.py" "server" ]