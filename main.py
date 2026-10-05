from fastapi import FastAPI

from src.persistence import DBDeps

app = FastAPI()


@app.get('/agents')
def get_agents(db: DBDeps):
    return db.getQualifiedAgents([])
