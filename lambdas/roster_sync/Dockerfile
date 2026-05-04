FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y gcc libpq-devel python3-devel && dnf clean all

COPY roster_sync/requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY shared/ shared/
COPY roster_sync/util/ util/
COPY roster_sync/handler.py handler.py

CMD ["handler.lambda_handler"]
