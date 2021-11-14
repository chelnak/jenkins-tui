FROM adoptopenjdk/openjdk11-openj9:alpine-slim

RUN apk update \
    && apk add bash git openssh dos2unix curl \
    && mkdir /root/.ssh \
    && chmod 0700 /root/.ssh \
    && ssh-keygen -A \
    && sed -i s/^#PasswordAuthentication\ yes/PasswordAuthentication\ no/ /etc/ssh/sshd_config \
    && sed -i -e "s/MACs /MACs hmac-sha1,/g" /etc/ssh/sshd_config \
    && echo "RSAAuthentication yes" > /etc/ssh/sshd_config \
    && echo "UsePAM yes" > /etc/ssh/sshd_config \
    && echo "PubkeyAuthentication yes" > /etc/ssh/sshd_config
USER root

ARG MAVEN_VERSION=3.6.3
ARG USER_HOME_DIR="/root"
ARG SHA=c35a1803a6e70a126e80b2b3ae33eed961f83ed74d18fcd16909b2d44d7dada3203f1ffe726c17ef8dcca2dcaa9fca676987befeadc9b9f759967a8cb77181c0
ARG BASE_URL=https://apache.osuosl.org/maven/maven-3/${MAVEN_VERSION}/binaries

RUN mkdir -p /opt/maven /opt/maven/ref \
  && echo "Downlaoding maven" \
  && curl -fsSL -o /tmp/apache-maven.tar.gz ${BASE_URL}/apache-maven-${MAVEN_VERSION}-bin.tar.gz \
  \
  && echo "Checking download hash" \
  && echo "${SHA}  /tmp/apache-maven.tar.gz" | sha512sum -c - \
  \
  && echo "Unziping maven" \
  && tar -xzf /tmp/apache-maven.tar.gz -C /opt/maven --strip-components=1 \
  \
  && echo "Cleaning and setting links" \
  && rm -f /tmp/apache-maven.tar.gz \
  && ln -s /opt/maven/bin/mvn /usr/bin/mvn

RUN addgroup -S jenkins && adduser -D agent -G jenkins
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

RUN git config --global user.name "Jenkins Java 11 Agent"
RUN git config --global user.email "java11.agent@jenkins.master"

EXPOSE 22

ENV JAVA_HOME /opt/java/openjdk
ENV MAVEN_HOME /opt/maven

RUN java --version
RUN mvn --version



ENTRYPOINT ["/entrypoint.sh"]

# -D in CMD below prevents sshd from becoming a daemon. -e is to log everything to stderr.
CMD ["/usr/sbin/sshd", "-D", "-e"]
