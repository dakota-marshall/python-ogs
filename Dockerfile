FROM python:3.11

WORKDIR /usr/src/app
COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["bash"]