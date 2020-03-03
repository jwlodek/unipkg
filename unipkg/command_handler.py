"""File for managing subprocess calls for unipkg
"""


import ctypes, os
from typing import List
from sys import platform
from subprocess import Popen, PIPE

WITH_PEXPECT=True

try:
    import pexpect
except ImportError:
    WITH_PEXPECT = False


def parse_string_into_executable_command(command : str, remove_quotes : bool) -> List[str]:
    """Function that takes in a string command, and parses it into a subprocess arg list
    Parameters
    ----------
    command : str
        The command as a string
    Returns
    -------
    run_command : list of str
        The command as a list of subprocess args
    """

    if '"' in command:
        run_command = []
        strings = re.findall('"[^"]*"', command)
        non_strings = re.split('"[^"]*"', command)
        for i in range(len(strings)):
            run_command = run_command + non_strings[i].strip().split(' ')
            string_in = strings[i]
            if remove_quotes:
                string_in = string_in[1:]
                string_in = string_in[:(len(string_in) - 1)]
            run_command.append(string_in)
        if len(non_strings) == (len(strings) + 1) and len(non_strings[len(strings)]) > 0:
            run_command.append(non_strings[len(strings) + 1])
    else:
        run_command = command.split(' ')

    return run_command



def handle_basic_command(command : str, remove_quotes : bool=True) -> (List[str], int):
    """Function that executes any git command given, and returns program output.
    Parameters
    ----------
    command : str
        The command string to run
    name : str
        The name of the command being run
    remove_quotes : bool
        Since subprocess takes an array of strings, we split on spaces, however in some cases we want quotes to remain together (ex. commit message)
    
    Returns
    -------
    out : str
        Output string from stdout if success, stderr if failure
    err : int
        Error code if failure, 0 otherwise.
    """

    out = None
    err = 0

    run_command = parse_string_into_executable_command(command, remove_quotes)
    try:
        proc = Popen(run_command, stdout=PIPE, stderr=PIPE)
        output, error = proc.communicate()
        if proc.returncode != 0:
            out = error.decode()
            err = proc.returncode
        else:
            out = output.decode()
    except:
        out = f"Unknown error processing command: {command}"
        err = -1
    return out, err


def handle_admin_command(command_str: str, passwd : str, expect : str) -> (List[str], int):
    if platform == 'win32':
        return handle_basic_command(command_str)
    else:
        command_str = f'sudo {command_str}'
        return None, None


def execute_command(command_str : str, is_admin_required : bool, passwd : str=None, expect : str='Password'):
    if is_admin_required == 'required':
        pass
        #return handle_admin_command(command_str, passwd, expect)
    else:
        return handle_basic_command(command_str)