import logging

import uvicorn
from starlette.responses import RedirectResponse

from notify_api import NotifyAPI
from notify_api.core.settings import get_api_settings


# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)  # the __name__ resolve to 'main' since we are at the root of the project.
# This will get the root logger since no logger in the configuration has this name.


app = NotifyAPI(bind=get_api_settings().NOTIFY_DATABASE_URL)


@app.get('/')
async def root():
    response = RedirectResponse(url='/docs')
    return response

if __name__ == '__main__':
    uvicorn.run(app, port=5002)
