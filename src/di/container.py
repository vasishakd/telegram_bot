"""Containers module."""

from pathlib import Path

from dependency_injector import containers, providers

from src.config import ConfigENV


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=['src.clients', 'src.db', 'src.web.routers.main', 'src.web.routers.api']
    )

    config = providers.Singleton(
        ConfigENV, _env_file=Path(__file__).parent / '../../.env'
    )
    database = providers.Singleton(object)
