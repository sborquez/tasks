from pydantic import Field

from tasks import get_logger, task, step, BaseParameters, BaseResult


logger = get_logger(__name__)


class Parameters(BaseParameters):
    name: str | None = Field(
        description="The name of the hello world branch",
        default=None,
    )

class Results(BaseResult):
    message: str = Field(
        description="The message to be printed",
    )


@step(name="Get Name", description="Generate a name")
def get_name(name: str ) -> str:
    logger.info(f"Getting name: {name}")
    return name


@step(name="Say Hello", description="Print a hello message")
def say_hello(name: str) -> str:
    logger.info(f"Hello, {name}!")
    return f"Hello, {name}!"


@task(name="Hello World", description="A hello world task")  # type: ignore
def hello_world(parameters: Parameters) -> Results:
    name = get_name(parameters.name or "")
    message = say_hello(name)
    return Results(message=message)
