from ninja import NinjaAPI
from learnhearApi.api import router as learnhearApi_router
from accounts.api import router as accounts_router
from lessons.api import router as lessons_router
from practices.api import router as practice_router


api = NinjaAPI()

api.add_router("/learnhearapi/", learnhearApi_router)
api.add_router("/accounts/", accounts_router)
api.add_router("/lessons/", lessons_router)
api.add_router("/practices/", practice_router)
