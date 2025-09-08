from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse
from collections.abc import Callable

def tw_response(voice_response: VoiceResponse) -> PlainTextResponse:
    fast_response = PlainTextResponse(str(voice_response))
    fast_response.headers['Content-Type'] = 'text/xml'
    return fast_response


def app_url(base_url: str) -> Callable[[str], str]:
    BASE_PATH = f'/{base_url}'

    def url_from(end_point: str) -> str:
        nonlocal BASE_PATH
        if end_point == '':
            return BASE_PATH
        return f'{BASE_PATH}/{end_point}'
    
    return url_from