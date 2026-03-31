FROM ubuntu:latest
LABEL authors="leoch"

ENTRYPOINT ["top", "-b"]