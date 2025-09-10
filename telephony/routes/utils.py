import os
import re
from fastapi import FastAPI, Request, Form, APIRouter
from fastapi.responses import PlainTextResponse
import httpx
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse,  Gather
from twilio.rest import Client

load_dotenv()
router = APIRouter()

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_phone = os.environ["TWILIO_PHONE_NUMBER"]

BASE_URL = 'https://922df4a5c81b.ngrok-free.app'


"""
Twilio will call this when the call ends (statusCallback).
You must configure the Twilio number with:
    Status Callback URL = https://<your-domain>/call-status
"""


@router.post("/message")
async def message():
    resp = VoiceResponse()
    resp.say('You will receive a SMS regarding your request shortly. ')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        # TODO pui linku de la frontend
        body='Check our platform for your specific form on your request: ',
        to="+40774596204",
        from_=str(twilio_phone)
    )
    return PlainTextResponse(str(resp), status_code=200, media_type="text/xml")


@router.post("/call-status")
async def call_status(request: Request) -> PlainTextResponse:
    form = await request.form()
    call_sid = form.get("CallSid")
    call_status = form.get("CallStatus")
    duration = form.get("CallDuration")
    call_number = form.get("From", "")

    global firstQuestion
    global message_case

    print(f"Call {call_sid} ended with status={call_status}, duration={duration}, call_number={call_number}")

    if call_status == "completed":
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{BASE_URL}/stop_call",
                    json={
                        'text': call_number
                    },
                    timeout=10
                )
            except Exception as e:
                print("Failed to forward end-of-call event:", e)

    firstQuestion = True
    message_case = 0

    return PlainTextResponse("", status_code=204)