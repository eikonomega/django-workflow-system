"""
Convenience Import/Export
"""
from .media_files import (
    workflow_step_media_location,
    collection_image_location,
    workflow_image_location,
    author_media_location,
)

# THIS IS FOR THE RESPONSE SCHEMA HANDLERS
# DEFINED HERE TO GET AROUND CIRCULAR DEPENDENCY ISSUE
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "stepInputID": {"type": "string", "format": "uuid"},
        "userInput": {},
    },
}
