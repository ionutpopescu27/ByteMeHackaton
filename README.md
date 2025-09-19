# ByteMe Hackaton Project

This project is a hackaton MVP for TechFest that demonstrates how Voice AI can improve customer service and reduce service costs in the insurance sector.

Many Insurance companies struggle with long wait times and high costs for the call center employees. Our solution comes in very handy automating redundant tasks like questions about the company policy, and generating lower overall maintenance costs. Human agents are still needed to handle complex support scenarios but would not need to worry about low level and priority calls.

It integrates speech recognition, retrieval-augmented generation (RAG), and conversational logic to handle common customer requests about the company policy.

The policy documents are uploaded via the web interface by the client insurance company, and stored into a local vector database(ChromaDB).

During a call, the bot queries this knowledge base to provide relevant answers for the customer questions about the company.

Transcripts are available after each call in the web dashboard for both the company and the customer such that the records of the calls are available at any time for further lookup.

# Tech Stack

Backend — FastAPI (Python): HTTP APIs for call orchestration, PDF ingestion, RAG queries.

RAG — Python + ChromaDB: Turning PDFs into retrievable knowledge (chunk → embed → store → retrieve).

Frontend — React: Demo UI (upload PDFs, view transcripts).

Telephony — Twilio: Real phone number, inbound calls.

# Call center flow

The customer dials the call center and will be asked to choose between 2 options using the keypad:

1 -> general purpose knowledge

2 -> specific questions on ByteMe Insurance

e.g. 1: General purpose knowledge

Q: *What documents do I need to submit when filing a claim?*
    
A: *Typically, you’ll need your policy number, a government-issued ID, proof of incident (such as a police report or medical report), and supporting bills or receipts.*

e.g. 2: Specific questions on ByteMe Insurance

2.1 - Asking specific questions about ByteMe insurance company

Q: *What is Motor Third Party Insurance claim process?*
    
A: *MOTOR THIRD PARTY (MTP) INSURANCE is a mandatory motor insurance cover required for all vehicles, vans, or motorcycles for private or commercial use, providing liability coverage against bodily injury or death of a third party.*

2.2. Sms + Form on specific needs 

Q:*I want to make a claim and i want the documents required to support a claim.*
    
A:*A sms was sent for your personalized form on your query, you will need to provide your identification, police accident report, and any other details the insurer may require to support your claim.*
    
2.3. Human escalation

Q: *I want to speak with an agent.*

A: *An agent will be in touch with you shortly.*

# Installation

The setup instructions are located in the README.md file from the backend directory of the project
