FROM python:alpine

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir .

CMD [ "quickweb" ]
