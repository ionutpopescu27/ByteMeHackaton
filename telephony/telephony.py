from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import httpx

app = FastAPI()


@app.post("/", response_class=PlainTextResponse)
async def root_fallback():
    return PlainTextResponse("<Response><Say>Missing /voice path.</Say></Response>",
                             media_type="text/xml")


# --- A) Built-in STT: voice webhook + handlers ---
@app.post("/voice", response_class=PlainTextResponse)
async def voice():
    twiml = """
<Response>
  <Gather input="speech" action="/handle-intent" partialResultCallback="/partial">
    <Say>Hi! Tell me what you need.</Say>
  </Gather>
  <Say>Sorry, I didn't catch that.</Say>
</Response>
""".strip()
    return PlainTextResponse(twiml, media_type="text/xml")

@app.post("/partial")
async def partial(request: Request):
    form = await request.form()
    print("Partial:", dict(form))  # shows partial transcripts in your terminal
    return PlainTextResponse("", status_code=204)

@app.post("/handle-intent", response_class=PlainTextResponse)
async def handle_intent(request: Request):
    form = await request.form()
    transcript = form.get("SpeechResult", "")
    confidence = form.get("Confidence")
    call_sid = form.get("CallSid")

    print("Transcript:", transcript)

    # 🔹 Forward to your friend’s ngrok endpoint
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://88cc1c106304.ngrok-free.app/rsp",
            json={
                  "text": transcript,
                }
        )

    # Respond back to Twilio so the caller hears something
    reply = f"You said: {transcript}"
    twiml = f"<Response><Say>{reply}</Say><Redirect>/voice</Redirect></Response>"
    return PlainTextResponse(twiml, media_type="text/xml")

