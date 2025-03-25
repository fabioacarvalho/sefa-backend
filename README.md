## Build container

```bash
docker build -t flask-api .
```

## Run container

```bash
fabioacarvalho@MacBook-Air-de-Fabio backend % docker run -v .:/app -p 8000:8000 flask-api
```