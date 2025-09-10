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

# Call Center flow process

```
               Bot responds with
Calling number ---------------->  - 1 -> general purpose knowledge              
                                  - 2 -> specific questions on ByteMe insurance  
                                        |
                                        |  
                                        |
                                        V
            1. Pressed '1'                                   
        Asking general questions
        about insurances
e.g. What documents do I need to submit when filing a claim?
          |
          |
          V
e.g Typically, you’ll need your policy number, a government-issued ID, proof of incident (such as a police report or medical report), and supporting bills or receipts. 

2. Pressed '2'

2.1. Asking specific questions about ByteMe insurance firm
e.g. What is Motor Third Party Insurance claim process?
                  |
                  |
                  V
MOTOR THIRD PARTY (MTP) INSURANCE is a mandatory motor insurance cover required for all vehicles, vans, or motorcycles for private or commercial use, providing liability coverage against bodily injury or death of a third party.

2.2. Sms + specific form on needs 
e.g.I want to make a claim and i want the documents required to support a claim.
Response: sms sent for your personalized form on your query , you will need to provide your identification, police accident report, and any other details the insurer may require to support your claim.

2.3. Human escalation 
e.g. I want to talk with an agent.

```

# Endpoints

- All personalized forms

```
GET http://127.0.0.1:8000/forms

Json Body Response:      
[
  {
    "id": "46679be6-1f4f-447e-a6e3-346ccb90e071",
    "conversation_id": "cec3a109-8c68-4974-a6b7-174d11fafc80",
    "questions": [
      "What is the date of the incident you are making a claim for?",
      "What type of insurance policy do you have?",
      "Can you provide a detailed description of what happened during the incident?",
      "Do you have a police report related to the incident?",
      "Are there any witnesses to the incident who can provide a statement?",
      "Do you have any photos or videos of the incident?",
      "Have you received any medical treatment as a result of the incident?",
      "Are there any other documents or evidence you have that can support your claim?"
    ],
    "locale": "en",
    "created_at": "2025-09-09T22:44:25.203393",
    "conversation": {
      "phone_number": null,
      "label": null,
      "started_at": "2025-09-09T22:44:18.703721",
      "ended_at": null
    }
  }
]
    
```

- All conversations based on phone number

```
POST: http://127.0.0.1:8000/conv
Json Body Request:
{
  "text": "+40774596204"
}
Json Body Response:
[
  {
    "id": "e325ba28-dd24-498a-9b29-4eb5235b4953",
    "phone_number": "+40774596204",
    "started_at": "2025-09-08T15:29:33.801919",
    "ended_at": "2025-09-08T15:33:00.229567",
    "messages": [
      {
        "id": "99ec3752-c8b1-4d16-ab50-86a4afe088b6",
        "role": "user",
        "text": "How long does it? Take bite me Insurance to process a claim?",
        "created_at": "2025-09-08T15:32:26.603637",
        "path_df": null,
        "number_page": null
      },
      {
        "id": "c97ba111-5208-4fb5-9822-e825fd6373af",
        "role": "bot",
        "text": "Claims are settled within sixty (60) days of reporting the incident, or within thirty (30) days after a dispute is resolved.",
        "created_at": "2025-09-08T15:32:26.614532",
        "path_df": "tmp_databases/Insurance.pdf",
        "number_page": 8
      },
      {
        "id": "bb925c07-2edf-4b0d-9edb-eef49fdd53cb",
        "role": "user",
        "text": "Can I bundle multiple insurance policies with bite me insurance?",
        "created_at": "2025-09-08T15:32:45.564029",
        "path_df": null,
        "number_page": null
      },
      {
        "id": "88233011-8e2c-4997-ad97-5bfe92db3792",
        "role": "bot",
        "text": "Yes, you can bundle multiple insurance policies with ByteMe Insurance.",
        "created_at": "2025-09-08T15:32:45.574275",
        "path_df": "tmp_databases/Insurance.pdf",
        "number_page": 14
      }
    ]
  },
  {
    "id": "184276c3-2447-4cf0-9458-97bb2a1b90ea",
    "phone_number": "+40774596204",
    "started_at": "2025-09-08T15:28:32.495750",
    "ended_at": "2025-09-08T15:29:33.791473",
    "messages": [
      {
        "id": "78a1ae1d-ce38-4d0b-80bd-db398622a479",
        "role": "user",
        "text": "How can I file an insurance claim with vitamin insurance?",
        "created_at": "2025-09-08T15:29:16.843795",
        "path_df": null,
        "number_page": null
      },
      {
        "id": "14c4fcb4-45e1-415e-aa25-a2aceb8720ef",
        "role": "bot",
        "text": "You need to report the accident to start the claim process and provide necessary details and documents to the insurer.",
        "created_at": "2025-09-08T15:29:16.853978",
        "path_df": "tmp_databases/Insurance.pdf",
        "number_page": 6
      }
    ]
  }
]
```

- Query on db + LLM response

```
POST : http://127.0.0.1:8000/rsp_db
Json Body Request: 
{
  "text": "Documents required to support a claim",
  "collection_name": "docs_824bea41-28d0-4a58-a459-bd50e857e6d2",
  "k": 3
}
Json Body Response:
{
  "text": "The documents required to support a claim are identification of the claimant and a police accident report."
}
```

- Save the pdfs to a chroma db collection

```
POST : http://127.0.0.1:8000/populate_chroma 
Json Body Request:
{
  "paths": ["/home/alex/projects/hackaton_endava/backend/tmp_databases/Insurance.pdf"]
}
Json Body Response:
{
  "text":"docs_824bea41-28d0-4a58-a459-bd50e857e6d2"
}
```

- Simple FAQ response from llm  

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
