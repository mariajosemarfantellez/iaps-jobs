FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# requirements python
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# copy all the code
COPY . .

EXPOSE 8000

ENTRYPOINT ["uvicorn", "main:app", "--port=8000", "--host=0.0.0.0", "--reload"]
