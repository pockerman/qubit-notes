from typing import Protocol

from pydantic import BaseModel


class PlatformHealth(BaseModel):
    reachable: bool
    providers: list[str] = []
    error: str | None = None


class StudyPlatform(Protocol):
    """The slice of the gogi platform the study assistant needs.

    The domain depends on this port only. ``GogiPlatform`` implements it with the gogi-python SDK, and the
    tests implement it in memory.
    """

    def health(self) -> PlatformHealth: ...
