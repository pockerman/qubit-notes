from sqlalchemy.engine import Engine

from qubit_notes.platform.port import StudyPlatform
from qubit_notes.settings import Settings


def platform_from(settings: Settings, engine: Engine) -> StudyPlatform:
    """the platform the settings name: the app's own, which keeps its material in the app's database, or gogi"""
    if settings.platform == "gogi":
        try:
            from qubit_notes.platform.gogi_adapter import GogiPlatform
        except ImportError as e:
            raise RuntimeError(
                "the gogi platform needs gogi-python: install it beside the app (make install-gogi)"
            ) from e
        return GogiPlatform(settings)
    from qubit_notes.platform.standalone import StandalonePlatform

    return StandalonePlatform(settings, engine)
