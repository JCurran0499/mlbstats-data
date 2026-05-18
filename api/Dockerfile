FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y gcc libpq-devel python3-devel && dnf clean all

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY adapter/ adapter/
COPY domain/ domain/
COPY main.py main.py

CMD ["main.handler"]
