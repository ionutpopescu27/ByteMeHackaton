from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import httpx

app = FastAPI()


@app.post("/", response_class=PlainTextResponse)
async def root_fallback():
    return PlainTextResponse("<Response><Say>Missing /voice path.</Say></Response>",
                             media_type="text/xml")


"""

route that gets triggered when the user calls -> listed under "When a call comes in" on the Twilio phone number

"""

@app.post("/voice", response_class=PlainTextResponse)
async def voice():
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
async def partial(request: Request):
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
async def handle_intent(request: Request):
    form = await request.form()
    transcript = form.get("SpeechResult", "")
    confidence = form.get("Confidence")
    call_sid = form.get("CallSid")

    print("Transcript:", transcript)

    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://3d6732d25766.ngrok-free.app/rsp",
            json={
                  "text": transcript,
                }
        )
        data = res.json()
        reply = data.get('text', "Sorry, I didn't get a reply.")

    twiml = f"""
<Response>
  <Say>{reply}</Say>
  <Redirect method="POST">/voice</Redirect>
</Response>
""".strip()
    return PlainTextResponse(twiml, media_type="text/xml")

