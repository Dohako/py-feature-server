import http
import fastapi
from pydantic import BaseModel


# using FASTAPI libraries create server on localhost:8080
# on receiving GET request from client that never connected before
# need to create a configuration dataclass.
# GET request will hold info about client, like ip, port, pod number, etc.. Also it will hold
# info about posessed env variables on client side, like FEATURE_1, FEATURE_2, etc.
# config file should consist of some basic info about client, like ip, port, pod number, etc.
# and simple configs like how often client should send data to server, how many times it should retry
api = fastapi.FastAPI()

class ClientsHello(BaseModel):
    ip: str
    port: int
    client_id: str
    features: dict[str, bool]


@api.post("/hello")
def root(client_hello: ClientsHello):
    print(client_hello)
    return {"request_offset": 0}

@api.get("/{client_id}/config")
def config(client_id: str):
    print(client_id)
    return {"config": "config"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(api, host="localhost", port=8080)
