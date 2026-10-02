from tests.simple_config import SimpleConfig
from fastapi import FastAPI

app = FastAPI(title = 'SimpleConfig')

@app.post("/visualize", response_model = SimpleConfig)
def visualize_schema(data: SimpleConfig):
  return data

#
# run server:
#   $ pipenv run uvicorn dev.fastapi:app --reload
#
# browse:
#   http://127.0.0.1:8000/docs
#
