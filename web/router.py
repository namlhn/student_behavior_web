from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router_web = APIRouter()

_base_dir = Path(__file__).resolve().parents[1]
_templates_dir = _base_dir / "web" / "templates"
if not _templates_dir.exists():
    _templates_dir = _base_dir / "templates"

templates = Jinja2Templates(directory=str(_templates_dir))


@router_web.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/ui/students")


@router_web.get("/ui/students", response_class=HTMLResponse)
async def ui_students(request: Request):
    return templates.TemplateResponse("students.html", {"request": request})


@router_web.get("/ui/faces", response_class=HTMLResponse)
async def ui_faces(request: Request):
    return templates.TemplateResponse("faces.html", {"request": request})


# Backward-compatible redirects from old static paths
@router_web.get("/ui/students.html", include_in_schema=False)
async def ui_students_html_compat():
    return RedirectResponse(url="/ui/students")


@router_web.get("/ui/faces.html", include_in_schema=False)
async def ui_faces_html_compat(request: Request):
    qs = request.url.query
    suffix = f"?{qs}" if qs else ""
    return RedirectResponse(url="/ui/faces" + suffix)
