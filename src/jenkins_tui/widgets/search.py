from __future__ import annotations

import re
from itertools import cycle
from random import choice
from typing import Any, Optional
from urllib.parse import unquote

from fast_autocomplete import AutoComplete, autocomplete_factory
from fast_autocomplete.misc import read_csv_gen
from rich.align import Align
from rich.color import ANSI_COLOR_NAMES
from rich.console import RenderableType
from rich.style import Style
from rich.text import Text
from textual import events
from textual.app import App
from textual.keys import Keys
from textual.message import Message, MessageTarget
from textual.reactive import Reactive, watch
from textual.widget import Widget
from textual.widgets import NodeID, TreeNode
from textual_inputs import TextInput
from textual_inputs.events import InputOnChange

from .. import styles
from .text_input_field import TextInputFieldWidget


def replace_last(string: str, find: str, replace: str) -> str:
    """Replace the last occurrence of a string."""
    reversed = string[::-1]
    replaced = reversed.replace(find[::-1], replace[::-1], 1)
    return replaced[::-1]


class SearchWidget(TextInputFieldWidget):

    autocompleter: AutoComplete = None
    value: Reactive[str] = Reactive("")
    predictions: cycle[str] = cycle([])
    current_prediction: Reactive[str] = Reactive("")
    last_word: Reactive[str] = Reactive("")

    def __init__(self) -> None:
        name = "search"
        title = Text("🔍 search")
        border_style = styles.PURPLE
        required = True
        super().__init__(
            name=name, title=title, border_style=border_style, required=required
        )

    async def on_mount(self) -> None:
        async def map(nodes: dict[NodeID, TreeNode]):
            _nodes = self.map_nodes(nodes=nodes)
            self.autocompleter = AutoComplete(words=_nodes)
            self.log("Searchable nodes have been mapped")

        watch(self.app, "searchable_nodes", map)

    async def handle_input_on_change(self) -> None:
        """Handle an InputOnChange message."""
        self.refresh()

    async def on_key(self, event: events.Key) -> None:

        await self.toggle_field_status(valid=True)
        search_string = self.value.split(" ")[-1]

        if event.key == Keys.Enter:
            event.stop()

            self.log(f"Searching for {self.value}")
            search_result = self.autocompleter.get_tokens_flat_list(
                word=self.value, max_cost=0, size=0
            )

            # if there are no results, we can't do anything so we return and set the widget border
            if not search_result:
                self.log(f"No results found for {self.value}")
                await self.toggle_field_status(valid=False)
                return

            word = self.autocompleter.words.get(self.value.strip().lower(), None)

            if not word:
                self.log(
                    f"No word match found for {self.value} words:\n{self.autocompleter.words}"
                )
                await self.toggle_field_status(valid=False)
                return

            node_id = word["id"]
            self.app.search_node = node_id

        elif event.key == "ctrl+i":
            self.current_prediction = next(self.predictions)

        elif event.key == Keys.Right:

            self.value = replace_last(
                self.value, self.last_word, self.current_prediction
            )
            self._cursor_position = len(self.value)
            self.last_word = self.current_prediction

        else:

            if not search_string:
                return

            search_result = self.autocompleter.get_tokens_flat_list(
                word=search_string,
            )

            if not search_result:
                return

            self.predictions = cycle(search_result)
            self.current_prediction = search_result[0]

        await self.post_message(InputOnChange(self))

    def _render_text_with_cursor(self) -> list[str | tuple[str, Style]]:
        """
        Produces the renderable Text object combining value and cursor
        """

        if len(self.value) == 0:
            segments = [self.cursor]

        elif self._cursor_position == 0:
            segments = [self.cursor, self._conceal_or_reveal(self.value)]

        elif self._cursor_position == len(self.value):
            prediction: str | Text = ""
            if len(self.current_prediction) > 0:

                words = self.value.split()
                if len(words) > 1:
                    self.last_word = words[-1]
                else:
                    self.last_word = self.value

                if (
                    self.current_prediction != self.last_word
                    and not self.value.endswith(" ")
                ):
                    prediction = Text(
                        self.current_prediction[len(self.last_word) :],
                        style=Style(dim=True, color="green"),
                    )
                else:
                    prediction = ""

            segments = [self.value, self.cursor, prediction]

        else:

            segments = [
                self._conceal_or_reveal(self.value[: self._cursor_position]),
                self.cursor,
                self._conceal_or_reveal(self.value[self._cursor_position :]),
            ]

        return segments

    def map_nodes(self, nodes: dict[NodeID, TreeNode]) -> dict[str, Any]:
        """Get the words from the csv file.
        In this case we are loading in a list of animals..
        """

        searchables: dict[str, Any] = {}
        for id, node in nodes.items():

            name = node.data.name.lower()
            if name != "root":
                searchables[name] = {"id": id}

        return searchables
