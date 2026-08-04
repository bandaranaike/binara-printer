# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from print_bill import router as bill_router
from print_summary import router as summary_router
from printer_control import router as printer_control_router
from security import validate_security_configuration

app = FastAPI()

# Do not start an unauthenticated printer agent.
validate_security_configuration()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Electron's main process does not need CORS. Keep this disabled for
    # browser origins; authentication is enforced separately on the routes.
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Print-Agent-Token"],
)

# Include routes from both modules
app.include_router(bill_router)
app.include_router(summary_router)
app.include_router(printer_control_router)
