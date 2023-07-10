FROM public.ecr.aws/lambda/python:3.10
ADD src/gitops.py /
ADD src/main.py /

RUN pip install ./requirement.txt -y

ENTRYPOINT ["/main.py"]
