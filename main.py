from http.client import HTTPResponse

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.database import create_table, get_client_features, create_client, update_client_features, \
    get_all_clients_features

api = fastapi.FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STANDARD_OFFSET = 5.5


class ClientsHello(BaseModel):
    ip: str
    port: int
    client_id: str
    features: dict[str, bool]


@api.post("/hello")
def hello_from_client(client_hello: ClientsHello):
    features = client_hello.features
    client_features = get_client_features(client_hello.client_id)
    if not client_features:
        create_client(client_hello.client_id, client_hello.ip, client_hello.port, STANDARD_OFFSET, features)
        client_features = get_client_features(client_hello.client_id)
    features_in_db = client_features.features
    if features_in_db != features:
        for f in features.keys():
            # we need to update features_in_db with new features and preserve old ones
            # also values from db should be above the new ones
            if f not in features_in_db:
                features_in_db[f] = features[f]

        update_client_features(client_hello.client_id, features_in_db)
        print(f"Warning: client {client_hello.client_id} features have changed")
    # check if we already have this client and preset feature list for him
    # if not, add him to the list
    # if we have him and features differ - update them, but also show a warning
    return {"request_offset": client_features.offset, "features": features_in_db},


@api.get("/{client_id}/config")
def config(client_id: str):
    features_model = get_client_features(client_id)
    if not features_model:
        return fastapi.Response(status_code=404)
    return {"request_offset": features_model.offset, "features": features_model.features}


@api.post("/{client_id}/config")
def config(client_id: str, features: dict[str, bool]):
    features_model = get_client_features(client_id)
    if not features_model:
        return fastapi.Response(status_code=404)
    update_client_features(client_id, features)
    return {"request_offset": features_model.offset, "features": features_model.features}


@api.get("/")
def get_clients():
    return get_all_clients_features()


if __name__ == "__main__":
    import uvicorn

    create_table()

    uvicorn.run(api, host="localhost", port=8080)
