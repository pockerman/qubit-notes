class StudyAssistantError(Exception):
    """A request qubit-notes refuses; the API maps each subclass to an HTTP status."""


class NotFound(StudyAssistantError):
    pass


class NotAllowed(StudyAssistantError):
    pass


class InvalidRequest(StudyAssistantError):
    pass


class Conflict(StudyAssistantError):
    pass


class TooLarge(StudyAssistantError):
    pass


class OutOfRange(StudyAssistantError):
    pass
