class StudyAssistantError(Exception):
    """A request the study assistant refuses; the API maps each subclass to an HTTP status."""


class NotFound(StudyAssistantError):
    pass


class NotAllowed(StudyAssistantError):
    pass


class InvalidRequest(StudyAssistantError):
    pass


class Conflict(StudyAssistantError):
    pass
