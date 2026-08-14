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

SAMPLE_YAML = """\
basics:
  name: "{{ name }}"
  email: "{{ email }}"
  phone: "{{ phone }}"
  location:
    city: "New York"
    region: "NY"
  summary: "Summary line here."
  profiles:
    - network: LinkedIn
      url: "{{ linkedin }}"
work:
  - name: "Company Name"
    description: "Role description here."
    position: "Engineer"
    startDate: 2020
    endDate: 2025
    highlights:
      - "Bullet one"
skills: []
education: []
"""

SAMPLE_YAML_INTEGRATION = """\
basics:
  name: "{{ name }}"
  email: "{{ email }}"
  phone: "{{ phone }}"
  location:
    city: "New York"
    region: "NY"
  summary: "Summary line here."
  profiles:
    - network: LinkedIn
      url: "{{ linkedin }}"
work:
  - name: "Company Name"
    description: "Role description here."
    position: "Engineer"
    startDate: 2020
    endDate: 2025
    highlights:
      - "Bullet one"
      - "Bullet two"
      - "Bullet three"
  - name: "Startup"
    position: "Junior Dev"
    startDate: 2015
    endDate: 2020
skills:
  - name: "Coding"
    keywords:
      - "Python"
education:
  - studyType: "B.Sc."
    area: "Computer Science"
    institution: "University"
"""

DUMMY_NAME = "John Doe"
DUMMY_EMAIL = "john@example.com"
DUMMY_PHONE = "555-123-4567"
DUMMY_LINKEDIN = "https://linkedin.com/in/johndoe"

DEFAULT_CONFIG = {"name": DUMMY_NAME, "email": DUMMY_EMAIL}
