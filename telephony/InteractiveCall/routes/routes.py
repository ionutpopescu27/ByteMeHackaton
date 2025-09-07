from fastapi import APIRouter, Request, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
# Local imports
from ..utils import app_url, tw_response
from .appointment_routes import router as appoint_router
from .inquires_routes import router as inq_router

router = APIRouter()
router.include_router(appoint_router)
router.include_router(inq_router)

# interactiveCall urls
ic_url = app_url('ic')
mock_reps = ["Hello, press 1 for inquires, or 2 for making an appointment.", "Hello I am your virtual assitant what can I help you with?", ""]


@router.post(ic_url('menu'))
async def main_menu(Digits:int = Form(None)) -> PlainTextResponse:
    controller = VoiceResponse()

    # if the digit is pressed
    if Digits:
        match Digits:
            case 1 : controller.redirect(ic_url('inquires'))
            case 2: controller.redirect(ic_url('appointment'))


    gather = Gather(input='dtmf', num_digits=1, timeout=30)
    gather.say(mock_reps[0])
    controller.append(gather)
    controller.hangup()
    return tw_response(controller)


