from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class PreferenceItem(BaseModel):
    preference_type: str
    preference_value: str


class PreferencesCreate(BaseModel):
    preferences: List[PreferenceItem]


class PreferenceResponse(BaseModel):
    id: int
    user_id: int
    preference_type: str
    preference_value: str

    class Config:
        from_attributes = True