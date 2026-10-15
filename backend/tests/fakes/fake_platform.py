from study_assistant.platform.port import PlatformHealth


class FakePlatform:
    """In-memory ``StudyPlatform`` for fast scenarios that need no gogi stack or API keys."""

    def __init__(self):
        self.providers = ["fake"]

    def health(self) -> PlatformHealth:
        return PlatformHealth(reachable=True, providers=list(self.providers))
