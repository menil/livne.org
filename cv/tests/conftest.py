"""Shared test constants and fixtures."""

SAMPLE_MD = """\
# John Doe

john@example.com

Summary line here.

## Experience

### Company Name
*Role description here.*

**Engineer | 2020-2025**

- Bullet one
"""

SAMPLE_MD_INTEGRATION = """\
# John Test

Summary line here.

## Experience

### Company Name
*Role description here.*

- Bullet one
- Bullet two
- Bullet three

## Education

- **B.Sc., Computer Science**, University
"""

DUMMY_NAME = "John Doe"
DUMMY_EMAIL = "john@example.com"
DUMMY_PHONE = "555-123-4567"
DUMMY_LINKEDIN = "https://linkedin.com/in/johndoe"
DUMMY_LOCATION = "New York, NY"

DEFAULT_CONFIG = {"name": DUMMY_NAME, "email": DUMMY_EMAIL}
