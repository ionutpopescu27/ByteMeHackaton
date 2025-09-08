# How to run? Steps

1. Fast Api  

```
uvicorn main:app --reload --port 8080
```

2. Ngrok server

```
ngrok http http://localhost:8080
```

3. Modify the endpoint in the Twilio phone number configs to the one that ngrok listens to
