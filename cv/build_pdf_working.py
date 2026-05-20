import markdown
import weasyprint
import re
import os
import sys

def fix_markdown_spacing(md_content):
    """
    Automatically injects required blank lines before Markdown lists 
    so the parser doesn't collapse them into a single paragraph.
    """
    lines = md_content.split('\n')
    out = []
    for i, line in enumerate(lines):
        # If line is a bullet point, and the previous line isn't empty or a bullet
        if line.strip().startswith('* ') and i > 0 and lines[i-1].strip() != '' and not lines[i-1].strip().startswith('* '):
            out.append('') # Inject the required blank line
        out.append(line)
    return '\n'.join(out)

def build_flawless_pdf(md_file):
    pdf_file = md_file.replace('.md', '.pdf')

    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found!")
        return

    # 1. Read and Auto-Format the Markdown
    with open(md_file, "r", encoding="utf-8") as f:
        raw_md = f.read()
    
    clean_md = fix_markdown_spacing(raw_md)

    # 2. Convert to pristine HTML
    html_body = markdown.markdown(clean_md, extensions=['tables', 'sane_lists'])

    # 3. TRANSLATION LAYER: Convert standard HTML to our Custom Layout
    
    # Fix Company Headers
    html_body = re.sub(
        r'<h3>(.*?)</h3>\s*<p><em>(.*?)</em></p>',
        r'<div class="company-header"><span class="company-name">\1</span><span class="company-desc">\2</span></div>',
        html_body, flags=re.DOTALL
    )

    # Fix Role Headers (Splits Title and Date so Date floats right)
    html_body = re.sub(
        r'<p><strong>(.*?)</strong>\s*\|\s*(.*?)</p>',
        r'<div class="role-header"><span class="role-title">\1</span><span class="role-date">\2</span></div>',
        html_body, flags=re.DOTALL
    )

    # Fix Skills & Early Career Tables
    html_body = re.sub(
        r'<li><strong>(.*?)</strong>:\s*(.*?)</li>',
        r'<tr><td class="skill-cat">\1</td><td class="skill-list">\2</td></tr>',
        html_body, flags=re.DOTALL
    )
    html_body = re.sub(r'<ul>(\s*<tr>)', r'<table class="skills-table">\1', html_body)
    html_body = re.sub(r'(</tr>\s*)</ul>', r'\1</table>', html_body)

    # Reduce spacing for the Early Career section
    html_body = re.sub(
        r'(<h2>Early Career History</h2>\s*)<table class="skills-table">',
        r'\1<table class="skills-table early-career">',
        html_body
    )

    # 4. Wrap in the exact CSS engine
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @page {{
            size: Letter;
            margin: 15mm 15mm;
            background-color: #fafbfd; 
        }}
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #333333;
            line-height: 1.45;
            margin: 0;
            padding: 0;
            font-size: 10pt;
        }}
        h1 {{
            font-size: 26pt;
            color: #1a252f;
            margin: 0 0 5px 0;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            text-align: center;
        }}
        h1 + p {{
            text-align: center;
            font-size: 10pt;
            color: #555555;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e0e6ed;
        }}
        h1 + p + p {{
            font-size: 10pt;
            margin-bottom: 20px;
            text-align: justify;
            padding: 0 5px;
        }}
        h2 {{
            font-size: 13pt;
            color: #2980b9;
            border-bottom: 1px solid #c8d6e5;
            padding-bottom: 4px;
            margin-top: 18px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .company-header {{
            margin-top: 12px;
            margin-bottom: 6px;
            page-break-after: avoid;
        }}
        .company-name {{
            font-size: 12pt;
            font-weight: bold;
            color: #1a252f;
        }}
        .company-desc {{
            font-style: italic;
            color: #666666;
            font-size: 9.5pt;
            display: block;
            margin-top: 2px;
        }}
        .role-header {{
            margin-top: 8px;
            margin-bottom: 4px;
            clear: both;
            page-break-after: avoid;
        }}
        .role-title {{
            font-weight: bold;
            color: #34495e;
            font-size: 10.5pt;
        }}
        .role-date {{
            float: right;
            font-weight: bold;
            color: #2980b9;
            font-size: 10pt;
        }}
        
        ul {{
            margin-top: 4px;
            margin-bottom: 12px;
            padding-left: 18px;
        }}
        li {{
            margin-bottom: 5px;
            text-align: justify;
        }}
        
        .skills-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 5px;
            margin-bottom: 15px;
        }}
        .skills-table td {{
            padding: 4px 0;
            vertical-align: top;
        }}
        .skill-cat {{
            font-weight: bold;
            width: 25%;
            color: #2c3e50;
        }}
        .skill-list {{
            width: 75%;
            color: #444444;
            text-align: justify;
        }}
        .early-career td {{
            padding: 2px 0;
        }}
    </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    # 5. Generate the final file
    print("Generating perfectly matched PDF...")
    weasyprint.HTML(string=full_html).write_pdf(pdf_file)
    print(f"Success! Created {pdf_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_pdf_working.py <input.md>")
        sys.exit(1)
    build_flawless_pdf(sys.argv[1])
