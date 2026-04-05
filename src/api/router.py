from src.api import auth, chat, crisis, screening, tracking

all_routers = [
    auth.router,
    chat.router,
    screening.router,
    tracking.router,
    crisis.router,
]
