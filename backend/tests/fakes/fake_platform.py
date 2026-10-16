from study_assistant.platform.port import PlatformHealth

SERVICES = ("gateway", "documents", "indexes", "llms", "prompts", "llm-sessions", "llm-tools", "guardrails")


class FakePlatform:
    """In-memory ``StudyPlatform`` for fast scenarios that need no gogi stack or API keys."""

    def __init__(self):
        self.reachable = True
        self.down: set[str] = set()

    def health(self) -> PlatformHealth:
        if not self.reachable:
            return PlatformHealth(reachable=False, error="UNAVAILABLE: connection refused")
        return PlatformHealth(
            reachable=True,
            services={name: "NOT_SERVING" if name in self.down else "SERVING" for name in SERVICES},
        )
