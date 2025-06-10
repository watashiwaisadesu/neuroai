from dataclasses import dataclass, field

@dataclass # Not frozen, as tokens_left changes. Could also be an Entity if more complex.
class BotQuota:
    """Manages token limits and usage."""
    token_limit: int = 500
    tokens_left: int = 50000

    def has_enough_tokens(self, amount: int) -> bool:
        return self.tokens_left >= amount

    def deduct(self, amount: int):
        if not self.has_enough_tokens(amount):
            raise ValueError("Insufficient tokens remaining")
        if amount < 0:
             raise ValueError("Cannot deduct negative tokens")
        self.tokens_left -= amount
