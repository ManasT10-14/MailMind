from pydantic import BaseModel, Field
from typing import Optional


class CalendarEventSchema(BaseModel):
    event_required: bool = Field(
        ...,
        description=(
            "Indicates whether a calendar event should be created "
            "based on the email content."
        ),
    )

    title: Optional[str] = Field(
        None,
        description=(
            "Short descriptive title of the event. "
            "Must be concise and directly derived from the email content. "
            "If event_required is False, this must be null."
        ),
    )

    date: Optional[str] = Field(
        None,
        description=(
            "Event date in ISO format (YYYY-MM-DD). "
            "Must be explicitly mentioned or unambiguously inferred. "
            "If unclear or missing, return null."
        ),
    )

    start_time: Optional[str] = Field(
        None,
        description=(
            "Event start time in 24-hour HH:MM format. "
            "Must not be guessed. Return null if missing."
        ),
    )

    end_time: Optional[str] = Field(
        None,
        description=(
            "Event end time in 24-hour HH:MM format if explicitly stated. "
            "If only duration is known, this may remain null."
        ),
    )

    duration_minutes: Optional[int] = Field(
        None,
        description=(
            "Duration of event in minutes if explicitly stated "
            "or clearly inferable (e.g., '30-minute call'). "
            "Return null if unknown."
        ),
    )

    timezone: Optional[str] = Field(
        None,
        description=(
            "Timezone of the event if explicitly mentioned (e.g., 'IST', 'PST'). "
            "Do not guess the timezone."
        ),
    )

    location: Optional[str] = Field(
        None,
        description=(
            "Location of the event (physical or virtual) if mentioned "
            "(e.g., Zoom link, Google Meet, office address)."
        ),
    )

    description: Optional[str] = Field(
        None,
        description=(
            "Brief event description summarizing the purpose of the meeting. "
            "Must be factual and concise."
        ),
    )

    clarification_required: bool = Field(
        ...,
        description=(
            "True if insufficient information is available to safely create the event. "
            "False if event details are complete and unambiguous."
        ),
    )

    clarification_message: Optional[str] = Field(
        None,
        description=(
            "If clarification_required is True, provide a short, polite message "
            "that can be sent to the user asking for the missing information. "
            "If clarification_required is False, return null."
        ),
    )

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description=(
            "Confidence score between 0 and 1 indicating reliability "
            "of the extracted event details."
        ),
    )
