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
    from_time: Optional[str] = None
    to_time: Optional[str] = None


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


class TrafficDashboardFilter(BaseModel):
    location: str
    from_time: str
    to_time: str


class TrafficSummary(BaseModel):
    wan_ip: str
    in_avg: Optional[float] = None
    out_avg: Optional[float] = None
    in_max: Optional[float] = None
    out_max: Optional[float] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class Session(BaseModel):
    session_id: str
    user_id: int
    login_time: datetime
    logout_time: Optional[datetime] = None
    wan_ip: str
    user_agent: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SessionResponse(BaseModel):
    message: str
    session_id: str
    login_time: datetime
    wan_ip: str
    user_agent: Optional[str] = None
    status: str


class ActivityLog(BaseModel):
    activity_id: Optional[int] = None
    session_id: str
    endpoint: str
    method: str
    timestamp: datetime
    status_code: Optional[int] = None
    request_payload_size: Optional[int] = None
    response_time_ms: Optional[int] = None
    created_at: Optional[datetime] = None


class LoginLogoutHistory(BaseModel):
    session_id: str
    user_id: int
    username: str
    login_time: datetime
    logout_time: Optional[datetime] = None
    wan_ip: str
    status: str


class SessionActivityReport(BaseModel):
    session_id: str
    login_time: datetime
    logout_time: Optional[datetime] = None
    user_id: int
    username: str
    wan_ip: str
    user_agent: Optional[str] = None
    session_duration_minutes: Optional[int] = None
    activities: List[ActivityLog]


class LogoutResponse(BaseModel):
    message: str
    session_id: str
    logout_time: datetime
    session_duration_minutes: int
