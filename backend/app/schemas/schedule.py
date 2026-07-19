"""Weekly working-hours schema.

Shared by hospital settings (opening hours) and doctor OPD schedules.
Stored in the database as JSON after validation.
"""

from datetime import time

from pydantic import BaseModel, ConfigDict, Field, model_validator

WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


class TimeSlot(BaseModel):
    """A single working period within a day, e.g. 09:00-13:00."""

    model_config = ConfigDict(extra="forbid")

    start: time
    end: time

    @model_validator(mode="after")
    def _end_after_start(self) -> "TimeSlot":
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self


class WeeklySchedule(BaseModel):
    """Working hours for each day of the week. Empty list means closed / off duty."""

    model_config = ConfigDict(extra="forbid")

    monday: list[TimeSlot] = Field(default_factory=list)
    tuesday: list[TimeSlot] = Field(default_factory=list)
    wednesday: list[TimeSlot] = Field(default_factory=list)
    thursday: list[TimeSlot] = Field(default_factory=list)
    friday: list[TimeSlot] = Field(default_factory=list)
    saturday: list[TimeSlot] = Field(default_factory=list)
    sunday: list[TimeSlot] = Field(default_factory=list)

    @model_validator(mode="after")
    def _no_overlapping_slots(self) -> "WeeklySchedule":
        for day in WEEKDAYS:
            slots = sorted(getattr(self, day), key=lambda slot: slot.start)
            for previous, current in zip(slots, slots[1:], strict=False):
                if current.start < previous.end:
                    raise ValueError(f"overlapping time slots on {day}")
        return self
