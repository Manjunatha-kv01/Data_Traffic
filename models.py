from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    id: Optional[int] = None
    username: str
    password: str
    user_display_name: Optional[str] = None
    status: Optional[int] = 1
    create_date: Optional[datetime] = None


class UserRegister(BaseModel):
    username: str
    password: str
    confirm_password: str
    user_display_name: Optional[str] = None


class UserProfile(BaseModel):
    id: Optional[int] = None
    username: str
    user_display_name: Optional[str] = None
    status: Optional[int] = None
    create_date: Optional[datetime] = None


class UserActivityFilter(BaseModel):
    wan_ip: str
    from_time: Optional[datetime] = None
    to_time: Optional[datetime] = None


class TrafficSummaryRequest(BaseModel):
    from_time: str
    to_time: str
    location: Optional[str] = None


class TrafficRequest(BaseModel):
    wan_ip: str
    from_time: str
    to_time: str


class TrafficData(BaseModel):
    ky: Optional[str] = None
    loo_bck: Optional[str] = None
    time_hour: datetime
    in_avg: Optional[float] = None
    out_avg: Optional[float] = None
    in_max: Optional[float] = None
    out_max: Optional[float] = None
    if_name: Optional[str] = None
    wan_ip: str
    if_descr: Optional[str] = None
    insert_time: Optional[datetime] = None


class TrafficSummary(BaseModel):
    wan_ip: str
    in_avg: Optional[float] = None
    out_avg: Optional[float] = None
    in_max: Optional[float] = None
    out_max: Optional[float] = None


class Token(BaseModel):
    access_token: str
    token_type: str
