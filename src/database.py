import sqlite3
from pydantic import BaseModel
from json import dumps, loads
import logging

try:
    from sqlalchemy import create_engine
    from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY = True
except ImportError:
    SQLALCHEMY = False


logging.basicConfig(level=logging.DEBUG)


class ClientModel(BaseModel):
    id: int
    client_id: str
    ip: str
    port: int
    offset: float
    features: dict[str, bool]


def create_table():
    logging.error("Creating table")
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    # create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS features
                    (id INTEGER PRIMARY KEY, client_id TEXT, ip TEXT, port INTEGER, offset_seconds FLOAT, features TEXT)''')
    conn.commit()
    conn.close()


def update_client_features(client_id, features):
    conn = sqlite3.connect('clients.db')
    logging.error(f"Updating client {client_id} features to {features}")
    c = conn.cursor()
    c.execute('SELECT * FROM features WHERE client_id=?', (client_id,))
    if c.fetchone():
        # TODO something wrong with types
        c.execute('UPDATE features SET features=? WHERE client_id=?', (features, client_id))
    else:
        c.execute('INSERT INTO features (client_id, features) VALUES (?, ?)', (client_id, features))
    conn.commit()
    conn.close()


def update_client_offset(client_id, offset):
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute('SELECT * FROM features WHERE client_id=?', (client_id,))
    if c.fetchone():
        c.execute('UPDATE features SET offset=? WHERE client_id=?', (offset, client_id))
    else:
        c.execute('INSERT INTO features (client_id, offset) VALUES (?, ?)', (client_id, offset))
    conn.commit()
    conn.close()


def get_client_features(client_id):
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute('SELECT * FROM features WHERE client_id=?', (client_id,))
    features = c.fetchall()
    conn.close()
    # TODO rework bellow
    if not features:
        return None
    features = features[0]
    new_features = ClientModel(id=features[0], client_id=features[1], ip=features[2], port=features[3], offset=features[4], features=loads(features[5]))
    # new_features.features = loads(new_features.features)
    return new_features


def get_all_clients_features():
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute('SELECT * FROM features')
    features = c.fetchall()
    conn.close()
    return [ClientModel(id=f[0], client_id=f[1], ip=f[2], port=f[3], offset=f[4], features=loads(f[5])) for f in features]


def create_client(client_id, ip, port, offset_seconds, features):
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute('INSERT INTO features (client_id, ip, port, offset_seconds, features) VALUES (?, ?, ?, ?, ?)', (client_id, ip, port, offset_seconds, dumps(features)))
    conn.commit()
    conn.close()


def create_table_sqlalchemy():
    engine = create_engine('sqlite:///clients.db', echo=True)
    metadata = MetaData()
    clients = Table('clients', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('name', String),
                    Column('email', String),
                    Column('phone', String),
                    Column('address', String)
                    )
    features = Table('features', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('client_id', Integer, ForeignKey('clients.id')),
                     Column('feature', String),
                     Column('value', String)
                     )
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
