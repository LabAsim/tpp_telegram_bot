FROM python:3.10.6
WORKDIR .
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Uncomment the following line. Add the desired values.
CMD ["python", "main.py", "--debug", "True", "--test", "True", "--mode", "self", "--dbpass", "changethispassword"]
