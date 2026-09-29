# Importing the models registers them on Base.metadata, which create_all needs.
from backend.app.models import category, transaction, user  # noqa: F401
