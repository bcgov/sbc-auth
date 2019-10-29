import uvicorn
from notify_api import NotifyAPI
from notify_api.core import config as AppConfig

app = NotifyAPI(bind=AppConfig.SQLALCHEMY_DATABASE_URI)

if __name__ == "__main__":
    uvicorn.run(app, port=5002)
