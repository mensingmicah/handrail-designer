"""The one base class for errors that mean "the inputs or registry need attention".

The CLI reports any InputError as a one-line message. Anything else is a
bug and keeps its full traceback.
"""


class InputError(ValueError):
    """The project file, a section, a dimension or the registry stops the calc."""
