"""Container-side runtime entrypoint for DevCapsule images."""

from .contract import RuntimePlan, RuntimePlanError

__all__ = ["RuntimePlan", "RuntimePlanError"]
