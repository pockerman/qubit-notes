from gogi.gogi import Gogi
from loguru import logger

from study_assistant.platform.port import PlatformHealth


class GogiPlatform:
    """``StudyPlatform`` implemented with the gogi-python SDK."""

    def __init__(self, gateway_url: str):
        self._gogi = Gogi(gateway_url=gateway_url, logger=logger)

    def health(self) -> PlatformHealth:
        health = self._gogi.health.status()
        return PlatformHealth(
            reachable=health.reachable,
            services={name: str(status) for name, status in health.services.items()},
            error=health.error,
        )
