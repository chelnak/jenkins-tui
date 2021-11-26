from __future__ import annotations

import re
from typing import Callable

from rich.console import Console


class Ask:
    """Ask provides an easy way to ask for input with some validation."""

    def __init__(self, console: Console | None = None) -> None:
        """Ask provides an easy way to ask for input with some validation.

        Args:
            console (Console | None): A Rich Console object. Defaults to None.
        """

        self.console = console if console else Console()

    def question(
        self,
        question: str,
        default: str | None = None,
        required: bool = True,
        end="",
        validation: str | Callable | None = None,
        password: bool = False,
    ) -> str:
        """Prompt for input using a predefined question.

        Args:
            question (str): The question to ask the user. This can be formatted with console markup from Rich (https://rich.readthedocs.io/en/latest/markup.html).
            default (str | None): The default value to use if the user doesn't provide one. Defaults to None.
            required (bool): Whether or not the user must provide a value. Defaults to True.
            end (str | None): The end of line character to use. Defaults to "".
            validation (str, Callable | None): A regex string to or callable to validate the user's input. Defaults to None.
            password (bool): Whether or not the user's input should be hidden. Defaults to False.

        Returns:
            str: The user's input.
        """

        try:

            if default:
                _question = f"{question} [[dim]{default}[/]]: {end}"
            else:
                _question = f"{question}: {end}"

            answer = self.console.input(_question, password=password)

            # If the user didn't enter anything, use the default
            if not answer and default:
                answer = default

            # If the user didn't enter anything and there is no default but the answer is required, ask again
            if not answer and not default and required:
                self.console.print(f"[red]This question is required.[/]")
                answer = self.question(
                    question, default, required, end, validation, password
                )

            # If the user entered something and validation is required but it doesn't match the regex or callable, ask again
            if validation:

                if callable(validation):
                    if not validation(answer):
                        self.console.print(
                            f"[red]Validation failed, the input didn't match the provided function![/]"
                        )
                        answer = self.question(
                            question, default, required, end, validation, password
                        )

                else:
                    match = re.match(validation, answer)
                    if not match:
                        self.console.print(
                            f"[red]Validation failed, the input didn't match the provided expression: ({validation})[/]"
                        )
                        answer = self.question(
                            question, default, required, end, validation, password
                        )

            return answer

        except KeyboardInterrupt:
            self.console.print("\n[red]Aborted![/]")
            exit(1)

        except:
            raise


if __name__ == "__main__":

    ask = Ask()

    def validator(input: str) -> bool:
        return input == "test"

    name = ask.question("What is your name?", validation=validator)
    age = ask.question("What is your age?", default="42", validation=r"^[0-9]+$")
    color = ask.question(
        "What is your favorite color?", default="blue", validation=r"^[a-z]+$"
    )

    print(name, age, color)
