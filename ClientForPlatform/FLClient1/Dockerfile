FROM python:3.12

RUN pip install poetry

COPY . .

RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "src/fl-client/main.py"]

#ENTRYPOINT ["top", "-b"]