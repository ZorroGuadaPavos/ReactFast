import traceback

try:
    from .users.models import User  # noqa
    from .items.models import Item  # noqa
except Exception:
    traceback.print_exc()
