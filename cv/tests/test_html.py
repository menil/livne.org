from src.html import build_html
from src.pdf import build_pdf


def test_company_header():
    html = "<h3>Acme Corp</h3>\n<p><em>Description</em></p>"
    result = build_pdf.transform_html(html)
    assert '<div class="company-header">' in result
    assert '<span class="company-name">Acme Corp</span>' in result
    assert '<span class="company-desc">Description</span>' in result


def test_role_header():
    html = "<p><strong>Engineer</strong> | 2020-2025</p>"
    result = build_pdf.transform_html(html)
    assert '<div class="role-header">' in result
    assert '<span class="role-title">Engineer</span>' in result
    assert '<span class="role-date">2020-2025</span>' in result


def test_skill_row():
    html = "<li><strong>Python</strong>: expert level</li>"
    result = build_pdf.transform_html(html)
    assert '<tr><td class="skill-cat">Python</td>' in result
    assert '<td class="skill-list">expert level</td></tr>' in result


def test_skills_table_wrap():
    html = "<ul>\n  <tr><td>a</td><td>b</td></tr>\n</ul>"
    result = build_pdf.transform_html(html)
    assert '<table class="skills-table">' in result
    assert "</table>" in result


def test_early_career_class():
    html = '<h2>Early Career History</h2>\n<table class="skills-table">'
    result = build_pdf.transform_html(html)
    assert 'class="skills-table early-career"' in result


def test_education():
    html = "<h2>Education</h2>\n<ul>\n<li>B.Sc., CS, University</li>\n</ul>"
    result = build_pdf.transform_html(html)
    assert '<div class="education">' in result
    assert "B.Sc., CS, University" in result


def test_no_op_for_plain_html():
    html = "<p>Hello world</p>"
    result = build_pdf.transform_html(html)
    assert result.strip() == html.strip()


def test_mailto_link():
    html = "<p>Contact me at user@example.com today.</p>"
    result = build_html.transform_html(html)
    assert '<a href="mailto:user@example.com">user@example.com</a>' in result
