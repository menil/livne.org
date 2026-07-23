# {{ basics.name }}
{{ basics.location.city }}, {{ basics.location.region }} | {{ basics.email }}{% if basics.phone %} | {{ basics.phone }}{% endif %}{% if basics.linkedin %} | {{ basics.linkedin }}{% endif %}

{{ basics.summary | trim }}

## Professional Experience

{% for comp in work -%}
### {{ comp.name }}
*{{ comp.description }}*

{% for role in comp.roles -%}
**{{ role.position }}** | {{ role.dates }}
{% for highlight in role.highlights -%}
* {{ highlight }}
{% endfor -%}
{% if not loop.last %}

{% endif -%}
{%- endfor %}
{% if not loop.last %}

{% endif -%}
{%- endfor %}

## Early Career History

{% for entry in early_career %}
* **{{ entry.dates }}**: {{ entry.details }}
{%- endfor %}

## Core Technologies & Architectures

{% for skill in skills %}
* **{{ skill.name }}**: {{ skill.keywords | join(', ') }}
{%- endfor %}

## Education

{% for edu in education %}
* **{{ edu.studyType }}, {{ edu.area }}**, {{ edu.institution }}
{%- endfor %}
