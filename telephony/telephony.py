from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import httpx
from twilio.twiml.voice_response import VoiceResponse,  Gather

app = FastAPI()
BASE_URL = 'https://490ad57e843e.ngrok-free.app'

@app.post("/", response_class=PlainTextResponse)
async def root_fallback():
    return PlainTextResponse("<Response><Say>Missing /voice path.</Say></Response>",
                             media_type="text/xml")


"""

route that gets triggered when the user calls -> listed under "When a call comes in" on the Twilio phone number

"""

firstQuestion : bool = True

@app.post("/voice", response_class=PlainTextResponse)
async def voice() -> PlainTextResponse:
    global firstQuestion
    resp = VoiceResponse()
    gather = Gather(input="speech", action="/handle-intent", partialResultCallback="/partial", timeout="5", speechTimeout="auto")

    if firstQuestion:
        gather.say('Hi! Tell me what you need.')
        firstQuestion = False
    else:
        gather.say('Can I help you with something else?')
    
    resp.append(gather)
    resp.say("Sorry, I didn't catch that.")

    return PlainTextResponse(str(resp), media_type="text/xml")

    twiml = """
<Response>
  <Gather input="speech" action="/handle-intent" partialResultCallback="/partial" timeout="5" speechTimeout="auto">
    <Say>Hi! Tell me what you need.</Say>
  </Gather>
  <Say>Sorry, I didn't catch that.</Say>
</Response>
""".strip()
    return PlainTextResponse(twiml, media_type="text/xml")



@app.post("/partial")
async def partial(request: Request) -> PlainTextResponse:
    form = await request.form()
    print("Partial:", dict(form))
    return PlainTextResponse("", status_code=204)



"""

params:
    request -> the voice input of the user who called

Sends caller input to the backend

returns:
    trasncript of what the caller said

"""


@app.post("/handle-intent", response_class=PlainTextResponse)
async def handle_intent(request: Request) -> PlainTextResponse:
    form = await request.form()
    transcript = form.get("SpeechResult", "")

    print("Transcript:", transcript)

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BASE_URL}/rsp",
            json={
                  "text": transcript
                },
                timeout=10
        )

        try:
            data = res.json()
        except Exception:
            print("Non-JSON response from backend:", res.text)
            data = {}

    reply = data.get('text', "Sorry, I didn't get a reply.")

    twiml = f"""
<Response>
  <Say>{reply}</Say>
  <Redirect method="POST">/voice</Redirect>
</Response>
""".strip()
    return PlainTextResponse(twiml, media_type="text/xml")



"""
Twilio will call this when the call ends (statusCallback).
You must configure the Twilio number with:
    Status Callback URL = https://<your-domain>/call-status
"""


@app.post("/call-status")
async def call_status(request: Request) -> PlainTextResponse:
    form = await request.form()
    call_sid = form.get("CallSid")
    call_status = form.get("CallStatus")
    duration = form.get("CallDuration")
    call_number = form.get("From", "")

    global firstQuestion

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

    return PlainTextResponse("", status_code=204)