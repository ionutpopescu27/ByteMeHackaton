# ByteMe Proiect Hackaton

1. Cum dai run la backend si ce endpoint-uri ? README.md din backend

** To run the fastapi server run **

uvicorn main:app --reload --port 8080


** To run the ngrok server run **

ngrok http http://localhost:8080

Then modify the endpoint in the Twilio phone number configs to the one that ngrok listens to