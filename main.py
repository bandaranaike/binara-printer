# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from print_bill import router as bill_router
from print_summary import router as summary_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.binara.live"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes from both modules
app.include_router(bill_router)
app.include_router(summary_router)
