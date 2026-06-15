FROM public.ecr.aws/lambda/python:3.12

COPY schedule_sync/requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY shared/ shared/
COPY schedule_sync/util/ util/
COPY schedule_sync/handler.py handler.py

CMD ["handler.lambda_handler"]
