# How to run

1. Basic setup

```
python3 -m venv .venv
Linux - source .venv/bin/activate || Windows - .venv\Scripts\activate
pip3 install -r req.txt
```

2. Setup the environment keys / models , make the **.env** file as in **env.example**

3. Run

```
fastapi dev main.py
```

# Endpoints

- Response from llm  

```
POST : http://127.0.0.1:8000/rsp
Json Body Request: 
{
  "text": "How can I file an insurance claim?"
}
Json Body Response: 
{
  "text":"You can file an insurance claim by contacting our claims department directly."
}
```

- Text to speech

```

POST : http://127.0.0.1:8000/tts
Json Body Request:
{
  "text": "How can I file an insurance claim?"
}
Json Body Response: 
{
  "path":"/home/alex/projects/hackaton_endava/backend/out/audio/56943cb325764722b95fb34cf0009107.mp3"
}
```

- Speech to text

```

POST: http://127.0.0.1:8000/speech
Json Body Request:
{
  "path": "/home/alex/projects/hackaton_endava/backend/out/audio/56943cb325764722b95fb34cf0009107.mp3"
}
Json Body Response:
{
  "text":"How can I file an insurance claim?"
}
```
