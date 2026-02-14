from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token, get_current_user, verify_password
from database import (
    get_user_by_username,
    create_user,
    user_exists_in_db,
    get_user_activity_by_wan_ip,
    get_traffic_summary_by_location,
    get_traffic_by_time_range
)
from models import UserRegister, UserActivityFilter, TrafficSummaryRequest, TrafficRequest

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Data Traffic API", "version": "1.0"}


@app.post("/register")
def register(user: UserRegister):
    if len(user.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if user_exists_in_db(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    success, message = create_user(user.username, user.password, user.user_display_name)
    if not success:
        raise HTTPException(status_code=500, detail=message)

    return {"message": "User registered successfully"}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/logout")
def logout():
    return {"message": "Logout successful (client should delete token)"}


@app.post("/traffic/summary")
def get_traffic_summary(data: TrafficRequest, user=Depends(get_current_user)):
    wan_ip = data.wan_ip
    from_time = data.from_time
    to_time = data.to_time

    if not wan_ip:
        raise HTTPException(status_code=400, detail="wan_ip is required")

    if not from_time or not to_time:
        raise HTTPException(status_code=400, detail="from_time and to_time are required")

    rows, count = get_traffic_by_time_range(wan_ip, from_time, to_time)

    if rows is None:
        raise HTTPException(status_code=500, detail="Database error")

    return {
        "starting_time": from_time,
        "ending_time": to_time,
        "status": "success" if count > 0 else "no data",
        "payload": {
            "no_of_rows": count,
            "data": rows
        }
    }


@app.post("/traffic/dashboard-summary")
def traffic_dashboard_summary(request: TrafficSummaryRequest, user=Depends(get_current_user)):
    summary = get_traffic_summary_by_location(
        from_time=request.from_time,
        to_time=request.to_time,
        location=request.location
    )

    return {
        "from_time": request.from_time,
        "to_time": request.to_time,
        "filter_location": request.location,
        "total_locations": len(summary),
        "summary": summary
    }

@app.post("/user/activity-history")
def user_activity_history(filters: UserActivityFilter, current_user=Depends(get_current_user)):
    data = get_user_activity_by_wan_ip(filters.wan_ip, filters.from_time, filters.to_time)

    return {
        "wan_ip": filters.wan_ip,
        "from_time": filters.from_time,
        "to_time": filters.to_time,
        "no_of_rows": len(data),
        "history": data
    }

