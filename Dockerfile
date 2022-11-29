FROM python

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /stripe

COPY ./requirements.txt /stripe/requirements.txt
RUN pip install -r /stripe/requirements.txt

COPY . /stripe

EXPOSE 8000
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]