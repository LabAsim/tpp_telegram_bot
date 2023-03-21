"""
A function to trace errors from traceback
"""
import os.path
import pathlib
import re
import traceback
from datetime import datetime
from colorama import *
from source.helper.misc import dir_path
from typing import Union


def file_exists(dir_path: Union[str, os.PathLike], name: str) -> bool:
    """Returns true if the path exists"""
    path_to_name = pathlib.Path(os.path.join(dir_path, name))
    if path_to_name.exists():
        return True
    else:
        return False


def strip_ansi_characters(text='') -> str:
    """https://stackoverflow.com/questions/48782529/exclude-ansi-escape-sequences-from-output-log-file"""
    try:
        ansi_re = re.compile(r'\x1b\[[0-9;]*m')
        return re.sub(ansi_re, '', text)
    except re.error as err:
        print(err)


def get_current_time() -> str:
    """
    :return: The current datetime as a string
    """
    time_now = datetime.now()
    dt = str(time_now.strftime("%d-%m-%Y %H:%M:%S")) + f'.{Fore.LIGHTBLACK_EX}{str(round(time_now.microsecond))[:4]}' \
                                                       f'{Style.RESET_ALL}'
    dt = f"[{dt}]\t"
    return dt


def cprint(text, to_print_time=True):
    """Prints and timestamps the text"""
    text = str(text)  # Be sure that text is a string.
    if to_print_time:
        print(f'{strip_ansi_characters(get_current_time())}{text}')
    elif not to_print_time:
        print(f'{text}')


def trace_error(to_print_error=True):
    """
    The function traces the exceptions by printing and logging the error.

    :param to_print_error: Boolean - If true, prints and logs. Else, its logs the errors in a separate txt file
    :return: None

    See also:
    # https://docs.python.org/3/library/traceback.html#traceback-examples
    """
    # exc_type, exc_value, exc_traceback = sys.exc_info()  # All the info from the exception
    formatted_lines = traceback.format_exc().splitlines()
    error_filepath = os.path.join(dir_path, 'errors.txt')
    error_data = ""
    # Alternative, just print and write traceback.format_exc()
    for line in formatted_lines:
        if to_print_error:
            cprint(line)
        if file_exists(dir_path, 'errors.txt'):
            with open(error_filepath, 'r+', encoding='utf-8') as file:
                file_contents = file.read()
                error_data = f'{file_contents}{strip_ansi_characters(get_current_time())} {line}\n'
            with open(error_filepath, 'w+', encoding='utf-8') as file:
                file.write(strip_ansi_characters(error_data))
        else:
            with open(error_filepath, 'w+', encoding='utf-8') as file:
                file.write(f"{strip_ansi_characters(get_current_time())}{line}\n")  # Add \n in the end to format nicely
    print(f"Errors saved in {error_filepath}")


if __name__ == "__main__":
    # Example for trace_error()
    try:
        a = 2
        a + "b"
    except Exception:
        trace_error()
