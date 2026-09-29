from decimal import Decimal
from typing import Annotated
from pydantic import PlainSerializer

# Amounts are stored and computed as Decimal. Pydantic would serialize Decimal
# as a JSON string ("10.00"); the frontend works with numbers, so responses
# emit them as JSON numbers instead.
Money = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]
