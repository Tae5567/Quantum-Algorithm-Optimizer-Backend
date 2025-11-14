from mangum import Mangum
from main import app

# Wrap FastAPI for Lambda
handler = Mangum(app, lifespan="off")