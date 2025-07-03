from .start import router as start_router
from .city_selection import router as city_selection_router
from .weather import router as weather_router
from .popular import router as popular_cities_router
# from .global_state_reset import router as global_state_reset_router

routers = [
    start_router,
    popular_cities_router,
    city_selection_router,
    weather_router,
]
