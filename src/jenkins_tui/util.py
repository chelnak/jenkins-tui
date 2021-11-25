def replace_last(string: str, find: str, replace: str) -> str:
    """Replace the last occurrence of a string."""
    reversed = string[::-1]
    replaced = reversed.replace(find[::-1], replace[::-1], 1)
    return replaced[::-1]
