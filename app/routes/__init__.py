from .projects import router as projects_router
from .tasks import router as tasks_router
from .agents import router as agents_router
from .milestones import router as milestones_router
from .users import router as users_router

__all__ = ["projects_router", "tasks_router", "agents_router", "milestones_router", "users_router"]
