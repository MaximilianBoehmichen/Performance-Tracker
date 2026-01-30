FROM ubuntu:latest
LABEL authors="Maximilian Böhmichen"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    texlive-full \
    latexmk \
    git \
    make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
CMD ["bash"]
