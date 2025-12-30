import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from app.core.plugins.loader import load_enabled_plugins, PluginLoadError

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

try:
    enabled_plugins = load_enabled_plugins()
    for plugin_instance in enabled_plugins:
        for router in plugin_instance.register_routers():
            app.include_router(
                router,
                prefix=f"{settings.API_V1_STR}/plugins/{plugin_instance.name}",
                tags=[plugin_instance.name],
            )
except PluginLoadError as e:
    print(f"PLUGIN LOAD FAILED (degraded mode): {e}")
    # app.state.plugin_load_error = str(e)  # Optional