class KeyInvalidError(Exception):
    """
    This key is invalid
    """
    pass

class NoValidKeyError(Exception):
    """
    No valid key in the pool
    """
    pass