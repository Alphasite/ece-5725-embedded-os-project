import os
import sys

import logging

import itertools
import traceback

import modules

def print_help(message, module):
    print()
    print(message)
    print_module(module, 1)


def print_module(module, depth):
    for name, module in module.items():
        print(" " * (depth * 2), "-", name)
        if not callable(module):
            print_module(module, depth + 1)


def parse_command(args, module, break_loop, settings):
    if len(args) == 0 or args[0] == "help":
        print_help("FIFO Tool", module)
        return

    command_path = args[0].split('.')
    arguments = args[1:]

    if command_path[0] == "exit":
        break_loop()
        return

    for i, arg in enumerate(command_path[:-1]):
        if arg in module:
            module = module[arg]
        else:
            path = ".".join(command_path[:i+1])
            print("Could not find module with path:", path)

            path = ".".join(command_path[:i])
            message = "modules in path: {}".format(path)
            print_help(message, module)

            return

    commands = command_path[-1].split("+")

    for command in commands:
        path = ".".join(itertools.chain(command_path[:-1], [command]))

        if command in module:
            command = module[command]
        else:
            print("Could not find command with path:", path)

            path = ".".join(itertools.chain(args[:-1]))
            message = "Options for {} are:".format(path)
            print_help(message, module)
            return

        # Zero length strings alias to the modules self.
        if not callable(command) and "" in command:
            command = command[""]

        if callable(command):
            print()
            print("===============================================================================================")
            print("Executing:", path)
            print("-----------------------------------------------------------------------------------------------")
            print()

            function_args = {}
            function_args["arguments"] = arguments

            try:
                return_val = command(settings, **function_args)

                if return_val:
                    print()
                    print("-----------------------------------------------------------------------------------------------")
                    print("Successfully executed:", path)
                    print("===============================================================================================")
                    print()
                else:
                    print()
                    print("-----------------------------------------------------------------------------------------------")
                    print("Error executing:", path)
                    print("===============================================================================================")
                    print()
                    return
            except:
                print()
                print("-----------------------------------------------------------------------------------------------")
                print("Encountered execution when executing:", path)
                print()
                traceback.print_exc(limit=None, file=None, chain=True)
                print()
                print("===============================================================================================")
                print()
                return

        else:
            print("Command not callable:", path)
            return


def run(settings):
    should_loop = True

    def break_loop() -> None:
        nonlocal should_loop
        should_loop = False

    verb = sys.argv[1]

    if "VERBOSE" in os.environ and os.environ["VERBOSE"].lower() == "true":
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if verb == "repl":
        while should_loop:
            command = input("> ")
            parse_command(command.split(), modules.MODULE, break_loop, settings)
    else:
        parse_command(sys.argv[1:], modules.MODULE, break_loop, settings)

if __name__ == '__main__':
    try:
        import settings_local as settings
        print("Imported local settings.")
    except ImportError:
        import settings
        print("Imported default settings.")

    run(settings)