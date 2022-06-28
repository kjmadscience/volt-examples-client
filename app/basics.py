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
    return {"Welcome to Client Server, visit /docs for Swagger UI"}

@app.post("/client/makeConfigFile")
async def make_config(request: Request, example: str, servers: str, display_interval: int, warm_up: int, duration: int, contestants: int, ratelimit: int, maxvotes: int, threads: Union[int, None] = None):
   templates = Jinja2Templates(directory="../templates/"+example)
   file = templates.get_template("run.sh.jinja").render({"request": request, "servers": servers, "display_interval": display_interval, "warm_up": warm_up, "duration": duration, "contestants": contestants, "ratelimit": ratelimit, "max_votes": maxvotes, "threads": threads})
   with open('../output/'+example+'/run.sh', "w") as f:
    print(file, file=f)
    return "Run file created Successfully"

@app.post("/client/SendConfigFile")
async def send_config(clientHost: str, example: str,zone: str) -> int:
    dest = "/opt/voltdb/examples/" + example + "/auto-run.sh"
    src = "../output/"+example+"/run.sh"
    os.system('gcloud compute scp ' + src + ' ' + clientHost + ':' + dest + ' --zone='+zone )
    return "Copied!"

@app.post("/client/StartRun")
async def start_Run(clientHost: str, example: str,zone: str, mode: str) -> int:
    command = "nohup sh /opt/voltdb/examples/"+example+"/auto-run.sh "+mode+" &"
    os.system('gcloud compute ssh root@'+clientHost+' --command="'+command+'" --zone='+zone)
    return "Run Started!"


@app.post("/volt/makeDepFile")
async def make_deploymentFile (request: Request, sites_per_host: Union[int, None] = None , k_factor: Union[int, None] = None, httpd_enabled: Union[bool, None] = None, snapshot_enabled: Union[bool, None] = None, commandlog_enabled: Union[bool, None] = None, cmdlog_size: Union[float, None] = None):
    templates = Jinja2Templates(directory="templates/")
    file = templates.get_template("deployment.xml.jinja").render({"request": request, "Siter per Host": sites_per_host, "K-Factor Safety value": k_factor, "HTTP daemon Enabled": httpd_enabled, "Snapshot Enabled": snapshot_enabled, "Commandlog Enabled": commandlog_enabled, "Commandlog Size": cmdlog_size })
    with open('output/deployment.xml', "w") as f:
        print(file, file=f)
        return "Deployment File created Successfully"

