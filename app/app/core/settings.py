from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "College IoT Project"
    debug: bool = True


settings = Settings()