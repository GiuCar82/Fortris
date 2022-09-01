FROM python:3.8-slim
RUN mkdir /opt/fortris
WORKDIR /opt/fortris
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD [ "python", "main.py" ]
CMD [ "uvicorn", "main:app", "--reload", "--host", "0.0.0.0" ]