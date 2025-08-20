FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy requirements.txt and install dependencies
COPY src/requirements.txt ./
RUN pip install -r requirements.txt

# Copy source code
COPY src/ .

ENV PORT=8080

# Run the web service on container startup using uvicorn
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
