from functools import wraps
from typing import Any, Callable

from tasks.db import (
    setup_context,
    create_or_check_job,
    get_context,
    update_job_status,
    update_job_step_status,
)
from tasks.types import (
    BaseParameters,
    BaseResult,
    TaskType,
    TaskWithJobIdType,
    StepType,
    StepExpection,
)
from tasks.utils import (
    get_logger,
    normalize_string,
)
from tasks.models import (
    JobError,
    StartJob,
    FailJob,
    FinishJob,
    StartJobStep,
    FinishJobStep,
    FailJobStep,
)

logger = get_logger(__name__)


def task(name: str, description: str) -> Callable[[TaskType], TaskWithJobIdType]:
    """Decorator to log execution status in Firestore."""
    def decorator(task_func: TaskType) -> TaskWithJobIdType:
        task_name = name
        task_id = normalize_string(task_name)
        task_description = description
        logger.debug(f"Adding {task_name} task")
        @wraps(task_func)
        def wrapper(job_id: str, parameters: BaseParameters) -> BaseResult | None:
            # Initialize Firestore client
            ctx = setup_context(job_id, task_id, parameters)

            # Log start
            create_or_check_job(ctx.db, ctx.job_id, ctx.task_id, ctx.parameters)
            logger.info(f"Starting task: {task_name}")
            try:
                # Run step
                update_job_status(ctx.db, ctx.job_id, StartJob())
                result = task_func(parameters)
            except StepExpection as e:
                # Log failure
                code = type(e.error).__name__
                message = str(e.error)
                additional_info = {"step": e.step_name}
                error = JobError(code=code, message=message, additional_info=additional_info)
                logger.error(f"Task {task_name} failed with error in step {e.step_name}: {error}")
            except Exception as e:
                # Log failure
                code = type(e).__name__
                message = str(e)
                additional_info = None
                error = JobError(code=code, message=message, additional_info=additional_info)
                logger.error(f"Task {task_name} failed with error: {error}")
                job_update = FailJob(error=error)
            else:
                job_update = FinishJob(result=result)

            # Log completion
            logger.info(f"Task {task_name} completed with status: {job_update.status}")
            update_job_status(ctx.db, ctx.job_id, job_update)
            return job_update.result
        # Add metadata to the wrapper
        wrapper.task_name = task_name  # type: ignore
        wrapper.task_description = task_description  # type: ignore
        return wrapper
    return decorator


def step(name: str, description: str) -> Callable[[StepType], StepType]:
    """Decorator to log execution status in Firestore."""
    def decorator(step_func: StepType) -> StepType:
        step_name = name
        step_description = description
        @wraps(step_func)
        def wrapper(*args, **kwargs) -> Any:
            # Get shared context
            ctx = get_context()

            # Log step start
            logger.info(f"Starting step: {step_name}")
            try:
                update_job_step_status(ctx.db, ctx.job_id, StartJobStep(name=step_name, description=step_description))
                step_result = step_func(*args, **kwargs)  # Run step
            except Exception as e:
                update_job_step_status(ctx.db, ctx.job_id, FailJobStep())
                raise StepExpection(
                    step_name=step_name,
                    error=e,
                ) from e
            else:
                logger.info(f"Step {step_name} completed")
                update_job_step_status(ctx.db, ctx.job_id, FinishJobStep())
                return step_result
        # Add metadata to the wrapper
        wrapper.step_name = step_name  # type: ignore
        wrapper.step_description = step_description  # type: ignore
        return wrapper
    return decorator
