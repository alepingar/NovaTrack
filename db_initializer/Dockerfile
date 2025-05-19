FROM python:3.12-slim

WORKDIR /app


COPY ./wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./populate_data.py .


CMD ["wait-for-it.sh", "mongo:27017", "-t", "60", "--strict", "--", "python", "populate_data.py"]