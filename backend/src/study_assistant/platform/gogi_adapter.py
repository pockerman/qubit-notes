import grpc
from gogi.gogi import Gogi
from loguru import logger

from study_assistant.platform.port import PlatformHealth


class GogiPlatform:
    """``StudyPlatform`` implemented with the gogi-python SDK."""

    def __init__(self, gateway_url: str):
        self._gogi = Gogi(gateway_url=gateway_url, logger=logger)

    def health(self) -> PlatformHealth:
        try:
            providers = self._gogi.llm_clients.get_llm_providers()
        except grpc.RpcError as e:
            return PlatformHealth(reachable=False, error=f"{e.code().name}: {e.details()}")
        return PlatformHealth(reachable=True, providers=[p.name for p in providers])
