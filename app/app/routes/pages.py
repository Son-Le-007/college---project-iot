from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.core.security import decode_access_token

router = APIRouter()

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    return decode_access_token(token) if token else None

@router.get("/", response_class=HTMLResponse)
async def home():
    return RedirectResponse(url="/login")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse(url="/dashboard")
    
    return request.app.state.templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={"request": request}
    )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    if get_current_user(request):
        return RedirectResponse(url="/dashboard")
        
    return request.app.state.templates.TemplateResponse(
        request=request, 
        name="register.html", 
        context={"request": request}
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login") 
        
    return request.app.state.templates.TemplateResponse(
        request=request, 
        name="dashboard.html", 
        context={"request": request, "email": user["sub"]}
    )
