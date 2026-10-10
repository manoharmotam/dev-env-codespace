FROM jenkins/jenkins:lts
USER root
RUN apt-get update -y \
    && apt-get install curl unzip -y \
    && curl -fsSL "https://awscli.amazonaws.com/v2/install.sh" | bash -s -- --system \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

USER jenkins