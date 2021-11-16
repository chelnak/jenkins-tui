FROM python:3.9-slim-buster

ENV JAVA_HOME /usr/bin/java

RUN apt-get update && \
    apt-get install -y git openssh-server openjdk-11-jdk\
      && mkdir /root/.ssh \
      && chmod 0700 /root/.ssh \
      && ssh-keygen -A \
      && sed -i s/^#PasswordAuthentication\ yes/PasswordAuthentication\ no/ /etc/ssh/sshd_config \
      && sed -i -e "s/MACs /MACs hmac-sha1,/g" /etc/ssh/sshd_config \
      && echo "RSAAuthentication yes" > /etc/ssh/sshd_config \
      && echo "UsePAM yes" > /etc/ssh/sshd_config \
      && echo "PubkeyAuthentication yes" > /etc/ssh/sshd_config

USER root

RUN addgroup --system jenkins
RUN adduser --disabled-password agent --ingroup jenkins
RUN echo "agent:Docker!" | chpasswd

RUN mkdir /home/agent/.ssh
RUN chmod 700 /home/agent/.ssh
RUN chown agent:jenkins /home/agent/.ssh

COPY --chown=agent:jenkins unsafe.pub /home/agent/.ssh/authorized_keys
RUN chmod 600 /home/agent/.ssh/authorized_keys

RUN mkdir /var/data
VOLUME /var/data

COPY entrypoint.sh /
RUN chmod u+x entrypoint.sh

RUN git config --global user.name "Jenkins Agent"
RUN git config --global user.email "jenkins.agent@jenkins.master"

EXPOSE 22

ENTRYPOINT ["/entrypoint.sh"]

# -D in CMD below prevents sshd from becoming a daemon. -e is to log everything to stderr.
CMD ["/usr/sbin/sshd", "-D", "-e"]
