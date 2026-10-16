from typing import Protocol

from pydantic import BaseModel


class PlatformHealth(BaseModel):
    reachable: bool
    # service name to its status, e.g. {"gateway": "SERVING", "llms": "NOT_SERVING"}
    services: dict[str, str] = {}
    error: str | None = None

    @property
    def serving(self) -> bool:
        return self.reachable and all(status == "SERVING" for status in self.services.values())


class StudyPlatform(Protocol):
    """The slice of the gogi platform the study assistant needs.

    The domain depends on this port only. ``GogiPlatform`` implements it with the gogi-python SDK, and the
    tests implement it in memory.
    """

    def health(self) -> PlatformHealth: ...
