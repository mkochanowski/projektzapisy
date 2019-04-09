FROM projektzapisy:base

COPY zapisy/ /vagrant/zapisy/

WORKDIR /vagrant/zapisy

RUN yarn
RUN apt-get -y install python3-pip
RUN pip3 install -r requirements.development.txt

ENV PYTHONPATH="$PYTHONPATH:/vagrant/zapisy"

RUN echo "alias python=python3" >> /home/vagrant/.bashrc
RUN echo "alias python=python3" >> /root/.bashrc

CMD [ "python3" "run.py" "server" ]
