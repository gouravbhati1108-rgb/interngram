from fastapi import APIRouter

from app.api.v1 import admin, auth, companies, discussions, internships, notifications, public, rankings, reviews, students

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(students.router)
api_router.include_router(companies.router)
api_router.include_router(internships.router)
api_router.include_router(reviews.router)
api_router.include_router(rankings.router)
api_router.include_router(discussions.router)
api_router.include_router(notifications.router)
api_router.include_router(admin.router)
api_router.include_router(public.router)
