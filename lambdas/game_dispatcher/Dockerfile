FROM public.ecr.aws/lambda/python:3.12

COPY game_dispatcher/requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY shared/ shared/
COPY game_dispatcher/util/ util/
COPY game_dispatcher/handler.py handler.py

CMD ["handler.lambda_handler"]
