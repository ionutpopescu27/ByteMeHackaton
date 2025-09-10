import os
import re
from fastapi import FastAPI, Request, Form, APIRouter
from fastapi.responses import PlainTextResponse
import httpx
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse,  Gather
from twilio.rest import Client


router = APIRouter()
BASE_URL = 'https://922df4a5c81b.ngrok-free.app'


"""

params:
    request -> the voice input of the user who called

Sends caller input to the backend, and returns a general purpose answer to the users question

returns:
    transcript of what the caller said

"""


message_case : int = 0

@router.post("/handle-intent-general", response_class=PlainTextResponse)
async def handle_intent_general(SpeechResult:str = Form(None)) -> PlainTextResponse:
    global message_case
    message : str = ''
    resp = VoiceResponse()

    gather = Gather(input="dtmf speech", partialResultCallback="/partial", timeout="5", speechTimeout="auto")

    data = {}

    if SpeechResult:
        print("SpeechResult:", SpeechResult)

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{BASE_URL}/rsp",
                    json={
                        "text": SpeechResult,
                        },
                        timeout=10
                )
                data = res.json()
        except Exception as e:
            body_preview = (res.text[:500] if "res" in locals() and hasattr(res, "text") else str(e))
            print("Backend error or non-JSON response:", body_preview)
        
    reply = data.get('text', "Sorry, I didn't get a reply")

    if message_case == 0:
        message = 'For general informations, you may state your question now'
        message_case = 1
    elif message_case == 1:
        message = f'{reply}. Do you need anything else? If not, you will be redirected shortly to the main menu'

    gather.say(message)
    resp.append(gather)
    # resp.say("Sorry, I didn't get a reply")
    resp.redirect(url='/voice', method="POST")


    return PlainTextResponse(str(resp), media_type="text/xml")



"""

params:
    request -> the voice input of the user who called

Sends caller input to the backend, and returns a more specific answer to the users question
See backend docs for a better understanding

returns:
    trasncript of what the caller said

"""


@router.post("/handle-intent-specific", response_class=PlainTextResponse)
async def handle_intent_specific(SpeechResult:str = Form(None)) -> PlainTextResponse:
    global message_case
    message : str = ''
    resp = VoiceResponse()

    gather = Gather(input="speech", partialResultCallback="/partial", timeout="5", speechTimeout="auto")

    data = {}

    if SpeechResult:
        print("SpeechResult:", SpeechResult)

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{BASE_URL}/rsp_db",
                    json={
                        "text": SpeechResult,
                        "collection_name": 'docs_824bea41-28d0-4a58-a459-bd50e857e6d2',
                        "k": 3
                        },
                        timeout=10
                )
                data = res.json()
        except Exception as e:
            body_preview = (res.text[:500] if "res" in locals() and hasattr(res, "text") else str(e))
            print("Backend error or non-JSON response:", body_preview)
        
    reply = data.get('text', "Sorry, I didn't get a reply")

    if re.search("sms", reply):
        resp.redirect('/message')

    if message_case == 0:
        message = 'For ByteMe insurance informations, you may state your question now'
        message_case = 1
    elif message_case == 1:
        message = f'{reply}. Do you need anything else? If not, you will be redirected shortly to the main menu'

    gather.say(message)
    resp.append(gather)
    # resp.say("Sorry, I didn't get a reply")
    resp.redirect(url='/voice', method="POST")


    return PlainTextResponse(str(resp), media_type="text/xml")


@router.post("/human-escalation-message")
async def human_escalation_message() -> PlainTextResponse:
    resp = VoiceResponse()
    resp.say('An agent will be with you shortly. Keep the call open to not loose your priority!')
    resp.redirect('/human-escalation-music')
    return PlainTextResponse(str(resp), media_type="text/xml")


@router.post("/human-escalation-music")
async def human_escalation_music() -> PlainTextResponse:
    resp = VoiceResponse()
    resp.play('https://drive.google.com/file/d/1iVIv9hO60rx7nT1eHIzO73h2MbcA_E_V/view?usp=drive_link', loop=3)
    resp.redirect('/human-escalation-message')
    return PlainTextResponse(str(resp), media_type="text/xml")


