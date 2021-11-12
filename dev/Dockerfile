FROM jenkins/jenkins

ENV JENKINS_OPTS -Djenkins.install.runSetupWizard=false
ENV CASC_JENKINS_CONFIG /usr/share/jenkins/ref/

COPY security.groovy /usr/share/jenkins/ref/init.groovy.d
COPY plugins.txt /usr/share/jenkins/ref/
COPY jenkins.yaml /usr/share/jenkins/ref/

RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt
RUN echo 2.0 > /usr/share/jenkins/ref/jenkins.install.UpgradeWizard.state

VOLUME /var/jenkins_home
