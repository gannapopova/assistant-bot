def parse_input(user_input: str):
    parts = user_input.strip().split()
    if not parts:
        raise ValueError("Empty input")
    cmd = parts[0].lower()
    args = parts[1:]
    return cmd, args
