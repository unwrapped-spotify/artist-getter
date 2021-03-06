FROM python

WORKDIR /src

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY *.py /src

CMD ["python", "source.py"]