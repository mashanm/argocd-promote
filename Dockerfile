FROM public.ecr.aws/lambda/python:3.11

RUN mkdir /app
COPY requirements.txt /app/
COPY src /app/

RUN pip install -r /app/requirements.txt

ENTRYPOINT ["/app/main.py"]
