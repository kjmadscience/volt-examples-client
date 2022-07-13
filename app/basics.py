from fastapi import Body, FastAPI
from pydantic import BaseModel
import yaml, os, jinja2
from typing import Union
from fastapi import Request
from fastapi.templating import Jinja2Templates



app = FastAPI()


@app.get("/")
async def root():
    return {"Welcome to Client Server, visit /docs for Swagger UI"}

@app.post("/client/makeConfigFile")
async def make_config(request: Request, example: str, servers: str, display_interval: int, warm_up: int, duration: int, contestants: int, ratelimit: int, maxvotes: int, threads: Union[int, None] = None):
   templates = Jinja2Templates(directory="../templates/"+example)
   file = templates.get_template("run.sh.jinja").render({"request": request, "servers": servers, "display_interval": display_interval, "warm_up": warm_up, "duration": duration, "contestants": contestants, "ratelimit": ratelimit, "maxvotes": maxvotes, "threads": threads})
   with open('../output/'+example+'/run.sh', "w") as f:
    print(file, file=f)
    return "Run file created Successfully"

@app.post("/client/SendConfigFile")
async def send_config(clientHost: str, example: str,zone: str) -> int:
    dest = "/opt/voltdb/examples/" + example + "/auto-run.sh"
    src = "../output/"+example+"/run.sh"
    os.system('gcloud compute scp ' + src + ' ' + clientHost + ':' + dest + ' --zone='+zone )
    return "Copied!"

@app.get("/client/StartRun")
async def start_Run(clientHost: str, example: str,zone: str, mode: str) -> int:
    command = "nohup sh /opt/voltdb/examples/"+example+"/auto-run.sh "+mode+" &"
    os.system('gcloud compute ssh root@'+clientHost+' --command="'+command+'" --zone='+zone)
    return "Run Started!"


@app.post("/volt/makeDepFile")
async def make_deploymentFile (request: Request, sites_per_host: Union[int, None] = None , k_factor: Union[int, None] = None, httpd_enabled: Union[str, None] = None, snapshot_enabled: Union[str, None] = None, commandlog_enabled: Union[str, None] = None, cmdlog_size: Union[float, None] = None):
    templates = Jinja2Templates(directory="templates/")
    file = templates.get_template("deployment.xml.jinja").render({"request": request, "sites_per_host": sites_per_host, "k_factor": k_factor, "httpd_enabled": httpd_enabled, "snapshot_enabled": snapshot_enabled, "commandlog_enabled": commandlog_enabled, "cmdlog_size": cmdlog_size })
    with open('output/deployment.xml', "w") as f:
        print(file, file=f)
        return "Deployment File created Successfully"

@app.post("/volt/SendDeploymentFile")
async def send_deployment_File (volt_hostnames: str, zone: str):
    source = "output/deployment.xml"
    dest = "/opt/voltdb/bin/"
    hostlist = volt_hostnames.split(",")
    for x in hostlist:
        os.system('gcloud compute scp '+source+' root@'+x+':'+dest+' --zone='+zone)

    return "Deployment File Copied"

@app.get("/volt/InitCluster")
async def Initialize_Volt_cluster(volt_hostnames: str, zone: str) -> int:
    command = "/opt/voltdb/bin/voltdb init -C /opt/voltdb/bin/deployment.xml --force"
    host = volt_hostnames.split(",")
    for x in host:
        os.system('gcloud compute ssh root@'+x+' --command="'+command+'" --zone='+zone)
    return "Volt Servers Initialized"

@app.get("/volt/StartCluster")
async def Start_Volt_cluster(volt_hostnames: str, zone: str) -> int:
    command = '/opt/voltdb/bin/voltdb start --host='+volt_hostnames+' &'
    host = volt_hostnames.split(",")
    for x in host:
        os.system('gcloud compute ssh root@'+x+' --command="'+command+'" --zone='+zone)
    return "Volt Cluster Started"

