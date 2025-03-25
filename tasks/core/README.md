# Core Module

This is the **Core Module** of the project, designed to handle essential workflows and tasks.

## Features

- Core functionality for workflows.
- Modular and reusable components.
- Easy to integrate with other modules.

## Decorators

Declare a sequential pipeline by defining a task function and step functions. Declare its I/O with BaseParameters and BaseResult.

- `task`: A decorator to define a task workflow.
- `step`: A decorator to define a step in a task.
- `BaseParameters`: Base class for task input parameters.
- `BaseResult`: Base class for task output result.


## Scripts

Use the following scripts to run the module, but make sure to install the concrete pipelines modules and point it with the environment variable `TASK_MODULE`.

- `TASK_MODULE`: The name of a concrete pipelines module.
```bash
export TASK_MODULE=hello_world
```

- `tasks-run`: Run the module with the concrete pipelines module.

```bash
export TASK_MODULE=hello_world
tasks-run --job_id <job_id> <... hello_world_parameters>
```

- `tasks-register`: Register the module with the concrete pipelines module in the database.

```bash
export TASK_MODULE=hello_world
tasks-register  --task_uri <cloud_run_job_path>
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.