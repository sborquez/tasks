from typing import Any, Callable

from pydantic import BaseModel


class StepExpection(Exception):
    def __init__(self, step_name: str, error: Exception):
        self.step_name = step_name
        self.error = error

class BaseParameters(BaseModel):
    """Base parameters for a task."""
    ...

class BaseResult(BaseModel):
    """Base result for a task."""
    ...


TaskType = Callable[[BaseParameters], BaseResult]
TaskWithJobIdType = Callable[[str, BaseParameters], BaseResult | None]
StepType = Callable[..., Any]
JobIDType = str
