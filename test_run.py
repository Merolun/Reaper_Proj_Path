# Author: Kevin PANCHOUT
# SPDX-License-Identifier: MIT
import pytest

from reaper_to_wwise import ProjectNotSavedError, WwiseRequestError, run

PROJECT = r"C:\Projects\Game\music.rpp"


class FakeWaapi:
    """In-memory stand-in for waapi-client."""

    def __init__(self, objects, reject_writes=False):
        self.objects = objects
        self.reject_writes = reject_writes
        self.writes = {}

    def call(self, uri, args=None, options=None):
        if uri == "ak.wwise.ui.getSelectedObjects":
            return {"objects": self.objects}
        if uri == "ak.wwise.core.object.setNotes":
            if self.reject_writes:
                return None  # waapi-client returns None when Wwise rejects a call
            self.writes[args["object"]] = args["value"]
            return {}
        raise AssertionError(uri)


def test_empty_note_receives_path():
    waapi = FakeWaapi([{"id": "A", "notes": ""}])
    assert run(PROJECT, waapi) == (1, 0)
    assert waapi.writes == {"A": PROJECT}


def test_existing_note_gets_path_on_next_line():
    waapi = FakeWaapi([{"id": "A", "notes": "kick layer"}])
    run(PROJECT, waapi)
    assert waapi.writes["A"] == "kick layer\n" + PROJECT


def test_path_already_present_is_skipped():
    waapi = FakeWaapi([{"id": "A", "notes": "kick\n" + PROJECT}])
    assert run(PROJECT, waapi) == (0, 1)
    assert waapi.writes == {}


def test_mixed_selection_counts():
    waapi = FakeWaapi([{"id": "A", "notes": PROJECT}, {"id": "B", "notes": ""}])
    assert run(PROJECT, waapi) == (1, 1)
    assert list(waapi.writes) == ["B"]


def test_rejected_write_raises_instead_of_reporting_success():
    waapi = FakeWaapi([{"id": "A", "notes": ""}], reject_writes=True)
    with pytest.raises(WwiseRequestError):
        run(PROJECT, waapi)


def test_empty_selection_returns_zero():
    assert run(PROJECT, FakeWaapi([])) == (0, 0)


@pytest.mark.parametrize("bad_path", ["", None])
def test_unsaved_project_raises_without_writing(bad_path):
    waapi = FakeWaapi([{"id": "A", "notes": ""}])
    with pytest.raises(ProjectNotSavedError):
        run(bad_path, waapi)
    assert waapi.writes == {}
