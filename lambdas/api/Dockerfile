FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y gcc libpq-devel python3-devel && dnf clean all

COPY api/requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY api/adapter/ adapter/
COPY api/main.py main.py

CMD ["main.handler"]
