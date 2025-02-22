FROM python

WORKDIR /app


COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["fastapi","dev","main.py","--host","0.0.0.0"]