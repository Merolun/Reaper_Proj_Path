# Author: Kevin PANCHOUT
# SPDX-License-Identifier: MIT
"""Write the current Reaper project path into the Notes of the objects selected in Wwise."""

import threading

WAAPI_URL = "ws://127.0.0.1:8080/waapi"
NOTE_SEPARATOR = "\n"
PATH_BUFFER_SIZE = 4096
CURRENT_PROJECT = -1
GET_SELECTED = "ak.wwise.ui.getSelectedObjects"
SET_NOTES = "ak.wwise.core.object.setNotes"  # Notes is not a regular property: setProperty rejects it


class ProjectNotSavedError(ValueError):
    """Raised when the Reaper project has no path on disk yet."""


class WwiseRequestError(RuntimeError):
    """Raised when Wwise rejects a WAAPI request."""


def _call(waapi, uri, args, **options):
    # waapi-client logs failures and returns None instead of raising
    result = waapi.call(uri, args, **options)
    if result is None:
        raise WwiseRequestError(f"Wwise rejected the request {uri}.")
    return result


def _merge_note(existing, path):
    """Return the note with path appended, or None if the path is already there."""
    if path in existing.splitlines():
        return None
    return existing + NOTE_SEPARATOR + path if existing else path


def _check_saved(project_path):
    if not isinstance(project_path, str) or not project_path:
        raise ProjectNotSavedError("The Reaper project has not been saved yet.")


def run(project_path, waapi):
    """Append project_path to the Notes of every object selected in Wwise.

    waapi is any object exposing call(uri, args, options=...) like waapi-client.
    Returns (updated, skipped); skipped objects already contained the path.
    Raises ProjectNotSavedError if project_path is empty or not a string.
    Raises WwiseRequestError if Wwise rejects a request (waapi returns None).
    On a WAAPI error midway, objects already written stay written.
    """
    _check_saved(project_path)
    selection = _call(waapi, GET_SELECTED, {}, options={"return": ["id", "notes"]})
    updated = skipped = 0
    for obj in selection.get("objects", []):
        note = _merge_note(obj.get("notes", ""), project_path)
        if note is None:
            skipped += 1
            continue
        _call(waapi, SET_NOTES, {"object": obj["id"], "value": note})
        updated += 1
    return updated, skipped


def _print(message):
    RPR_ShowConsoleMsg(message + "\n")  # noqa: F821 (injected by Reaper)


def _reaper_project_path():
    return RPR_EnumProjects(CURRENT_PROJECT, "", PATH_BUFFER_SIZE)[2]  # noqa: F821


def _update_wwise(project_path):
    from waapi import WaapiClient

    _check_saved(project_path)  # report an unsaved project before trying to connect
    with WaapiClient(url=WAAPI_URL) as client:
        return run(project_path, client)


def _in_worker_thread(func, *args):
    """Run func in a worker thread; return its result or re-raise its error."""
    outcome = {}

    def target():
        try:
            outcome["value"] = func(*args)
        except BaseException as error:  # re-raised in the caller's thread
            outcome["error"] = error

    thread = threading.Thread(target=target)
    thread.start()
    thread.join()
    if "error" in outcome:
        raise outcome["error"]
    return outcome["value"]


def main():
    try:
        from waapi import CannotConnectToWaapiException
    except ImportError:
        _print("waapi-client is missing. Run: pip install waapi-client")
        return
    try:
        # Reaper's embedded Python makes asyncio's set_wakeup_fd fail in the main thread
        updated, skipped = _in_worker_thread(_update_wwise, _reaper_project_path())
    except ProjectNotSavedError as error:
        _print(f"{error} Save it, then run this script again.")
    except CannotConnectToWaapiException:
        _print("Cannot reach Wwise. Start Wwise and enable WAAPI (Project > User Preferences).")
    except WwiseRequestError as error:
        _print(f"{error} Some objects may already be updated. See the Wwise WAAPI log.")
    else:
        if updated + skipped == 0:
            _print("No object selected in Wwise: nothing updated.")
        else:
            _print(f"Wwise: {updated} object(s) updated, {skipped} already up to date.")


if __name__ == "__main__":
    main()
