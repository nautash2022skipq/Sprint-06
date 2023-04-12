FROM thoom/pyresttest

WORKDIR /app

COPY ./tests .

ARG url
ARG file

ENV url_env=${url}
ENV file_env=${file}

ENTRYPOINT pyresttest ${url_env} ${file_env}