from fastapi import APIRouter, Request, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
# Local imports
from ..utils import app_url, tw_response

router = APIRouter()
# interactiveCall urls
ic_url = app_url('ic/inquires')
mock_reps = ["Hello, press 1 for inquires, or 2 for making an appointment.", "Hello I am your virtual assitant what can I help you with?", "Hello, We are very pleased that you choosed us for the insurance, some information must be provided before making the appointment"]



@router.post(ic_url(''))
async def inquiry():
    controller = VoiceResponse()

    gather = Gather(input='speech', action=ic_url('process'), loop=3)
    gather.say(mock_reps[1])
    controller.append(gather)
    # redirecting the person back to the main menu in case no response is provided
    controller.redirect(ic_url('menu'))

    return tw_response(controller)

