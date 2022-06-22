from fastapi import FastAPI
from pydantic import BaseModel
import yaml, os, jinja2
from typing import Union
from fastapi import Request
from fastapi.templating import Jinja2Templates

class config(BaseModel):
    volt_hostnames: str
    client_hostname: str

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")  # Path parameters
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/configs/yaml") # take input from user and write in YAML
async def create_config(config: config):
    config_dict = config.dict()
    with open("../config/var.yaml", "w") as stream:
        print(yaml.safe_dump(config_dict, stream))
    return config_dict




templates = Jinja2Templates(directory="../templates/voter/")
@app.post("/client/config")
async def make_config(request: Request, servers: str, display_interval: int, warm_up: int, duration: int, contestants: int, ratelimit: int, maxvotes: int, threads: Union[int, None]):
   # templates.TemplateResponse("run.sh.jinja", {"request": request, "servers": servers, "display_interval": display_interval, "warm_up": warm_up, "duration": duration, "contestants": contestants, "ratelimit": ratelimit, "max_votes": maxvotes, "threads": threads})
   #template = templateEnv.get_template(TEMPLATE_FILE)
   file = templates.get_template("run.sh.jinja").render({"request": request, "servers": servers, "display_interval": display_interval, "warm_up": warm_up, "duration": duration, "contestants": contestants, "ratelimit": ratelimit, "max_votes": maxvotes, "threads": threads})
   with open('../output/voter/run.sh', "w") as f:
    print(file, file=f)
    msg = "Bonsoir Elliot"
    return msg