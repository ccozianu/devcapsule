"""The capsule web console: the ``devcapsule`` commands' reports as pages.

The package is a FastAPI application plus a static tree. It runs beside the
runtime as its own process, reads the mounted project, and calls the runtime
CLI's ``--json`` outputs as its API. It never imports the runtime's code.
"""

__version__ = "0.1.0"
