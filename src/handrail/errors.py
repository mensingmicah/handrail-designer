"""The one base class for errors that mean "the inputs or registry need attention".

The CLI reports any InputError as a one-line message. Anything else is a
bug and keeps its full traceback.

Every InputError is a stop: a place the tool refuses to compute and says
why. Each carries the id of its stop (stops.Stop), which is how
docs/brief/stops.md and tests/test_stops.py name it. The id is required,
so no stop can be added without one.
"""

from handrail.stops import Stop


class InputError(ValueError):
    """The project file, a section, a dimension or the registry stops the calc."""

    def __init__(self, message: str, *, stop: Stop):
        super().__init__(message)
        self.stop = Stop(stop)


class SectionStop(InputError):
    """A hard stop: the tool will not check this section (slender, or out of range)."""
