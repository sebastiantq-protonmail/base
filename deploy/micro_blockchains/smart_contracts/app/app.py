from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Config modules import
from app.api.config.env import API_NAME, PRODUCTION_SERVER_URL, DEVELOPMENT_SERVER_URL, LOCALHOST_SERVER_URL
from app.api.config.limiter import limiter
from app.api.config.dag import get_blockchain

# Routes import
from app.api.routes.smart_contracts import router as smart_contracts
from app.api.routes.transactions import router as transactions

title=f'{API_NAME} API'
description=f'{API_NAME} API description.'
version='1.0.1'
servers=[
    {"url": LOCALHOST_SERVER_URL, "description": "Localhost server"},
    {"url": DEVELOPMENT_SERVER_URL, "description": "Development server"},
    {"url": PRODUCTION_SERVER_URL, "description": "Production server"},
]
terms_of_service = ''
contact = {
    'name': '',
    'url': '',
    'email': '',
}
license_info = {
    'name': 'MIT',
    'url': 'https://opensource.org/licenses/MIT',
}

app = FastAPI(
    openapi_url=f'/api/v1/{API_NAME}/openapi.json',
    docs_url=f'/api/v1/{API_NAME}/docs',
    redoc_url=f'/api/v1/{API_NAME}/redoc',
    servers=servers,
    title=title,
    description=description,
    version=version,
    terms_of_service=terms_of_service,
    contact=contact,
    license_info=license_info,
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=title,
        version=version,
        description=description,
        routes=app.routes,
        servers=servers,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "..." # Add your logo URL here
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware configuration
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.on_event('startup')
async def on_startup():
    blockchain = get_blockchain()

    # Actions to be executed when the API starts.
    print('API started')

@app.on_event('shutdown')
async def on_shutdown():
    # Actions to be executed when the API shuts down.
    print('API shut down')

# Include the routes
app.include_router(smart_contracts, prefix=f'/api/v1/{API_NAME}')
app.include_router(transactions, prefix=f'/api/v1/{API_NAME}/transactions')
