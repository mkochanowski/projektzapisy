ARG IMAGE_VERSION
FROM python:${IMAGE_VERSION}
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN pip install wheel
RUN mkdir -p /app
WORKDIR /app
EXPOSE 8000