# This class defines a decorator, used to render views
# depending on a condition
# pylint: disable=invalid-name,too-few-public-methods
class condec:
    def __init__(self, dec, condition):
        self.decorator = dec
        self.condition = condition

    def __call__(self, func):
        if not self.condition:
            # Return the function unchanged, not decorated.
            return func
        return self.decorator(func)
