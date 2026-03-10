from colorama import Fore, init

init(autoreset=True)


def input_error(handler):
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except ValueError as e:
            return f"{Fore.RED}Invalid arguments. {e}"
        except KeyError:
            return f"{Fore.RED}Contact not found."
        except IndexError:
            return f"{Fore.RED}Not enough arguments."
    return wrapper
