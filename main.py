from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token, get_current_user, verify_password
from database import (
    get_user_by_username,
    create_user,
    user_exists_in_db,
    get_user_activity_by_wan_ip,
    get_traffic_dashboard_by_location_wanip,
    get_traffic_dashboard_by_location,
    get_traffic_by_time_range,
    create_session,
    close_session,
    create_access_log
)
from models import UserRegister, TrafficRequest, TrafficDashboardFilter

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Data Traffic API", "version": "1.0"}


# ------------------- MIDDLEWARE (ACCESS LOGGING) -------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)

    try:
        if request.url.path in ["/login", "/register", "/logout", "/"]:
            return response

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return response

        token = auth_header.split(" ")[1]
        payload = get_current_user(token, raw_payload=True)

        session_id = payload.get("session_id")
        user_id = payload.get("user_id")

        if session_id and user_id:
            create_access_log(
                session_id=session_id,
                user_id=user_id,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                wan_ip=request.client.host
            )
    except Exception as e:
        print("Access log error:", e)

    return response


# ------------------- AUTH APIs -------------------

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
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    wan_ip = request.client.host
    user = get_user_by_username(form_data.username)

    # -------- LOGIN FAILURE LOGGING --------
    if not user or not verify_password(form_data.password, user["password"]):
        create_access_log(
            session_id=None,
            user_id=user["id"] if user else None,
            endpoint="/login",
            method="POST",
            status_code=401,
            wan_ip=wan_ip
        )
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # -------- LOGIN SUCCESS --------
    session_id = create_session(user["id"], user["username"], wan_ip)
    if not session_id:
        raise HTTPException(status_code=500, detail="Failed to create session")

    token = create_access_token({
        "sub": user["username"],
        "session_id": session_id,
        "user_id": user["id"]
    })

    create_access_log(
        session_id=session_id,
        user_id=user["id"],
        endpoint="/login",
        method="POST",
        status_code=200,
        wan_ip=wan_ip
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "session_id": session_id
    }


@app.post("/logout")
def logout(current_user=Depends(get_current_user)):
    session_id = current_user.get("session_id")
    if session_id:
        close_session(session_id)
    return {"message": "Logout successful"}


# ------------------- BUSINESS APIs -------------------

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


@app.post("/traffic/location-wanip-summary")
def traffic_location_wanip_summary(filters: TrafficDashboardFilter, current_user=Depends(get_current_user)):
    if not filters.location:
        raise HTTPException(status_code=400, detail="location is required")
    if not filters.from_time or not filters.to_time:
        raise HTTPException(status_code=400, detail="from_time and to_time are required")

    data = get_traffic_dashboard_by_location(
        filters.location,
        filters.from_time,
        filters.to_time
    )

    if not data:
        return {
            "location": filters.location,
            "from_time": filters.from_time,
            "to_time": filters.to_time,
            "summary": [],
            "message": "No data found for given location and time range"
        }

    return {
        "location": filters.location,
        "from_time": filters.from_time,
        "to_time": filters.to_time,
        "total_records": len(data),
        "summary": data
    }
