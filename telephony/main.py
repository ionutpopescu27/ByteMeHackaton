from  fastapi import FastAPI
from .InteractiveCall.routes.routes import router

app = FastAPI()
# Adding the routes related to the interactive voice call 
app.include_router(router)