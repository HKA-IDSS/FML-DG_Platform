FROM python:3.10.12

EXPOSE 5100:5100

# System deps:
RUN pip install poetry

# Copy only requirements to cache them in docker layer
WORKDIR /code

## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.11.0/wait /wait
RUN chmod +x /wait

COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false && poetry install
# Creating folders, and files for a project:
COPY . /code

RUN chmod +x ./start.sh
CMD /wait && sh ./start.sh