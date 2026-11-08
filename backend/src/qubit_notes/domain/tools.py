"""What can be attached to a subject, to appear where its material is read or written
(features/subject_tools.feature)."""

from pydantic import BaseModel


class Tool(BaseModel):
    id: str
    name: str
    # what sort of tool it is, e.g. a compiler
    kind: str


TOOLS = [
    Tool(id="go", name="Go compiler", kind="compiler"),
    Tool(id="python", name="Python interpreter", kind="interpreter"),
]
