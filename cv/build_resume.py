import weasyprint

html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
    @page {
        size: Letter;
        margin: 15mm 15mm;
        background-color: #fafbfd; /* Very subtle cool off-white for a tech-forward feel */
    }
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #333333;
        line-height: 1.45;
        margin: 0;
        padding: 0;
        font-size: 10pt;
    }
    h1 {
        font-size: 26pt;
        color: #1a252f;
        margin: 0 0 5px 0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        text-align: center;
    }
    .contact-info {
        text-align: center;
        font-size: 10pt;
        color: #555555;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid #e0e6ed;
    }
    .summary {
        font-size: 10pt;
        margin-bottom: 20px;
        text-align: justify;
        padding: 0 5px;
    }
    h2 {
        font-size: 13pt;
        color: #2980b9;
        border-bottom: 1px solid #c8d6e5;
        padding-bottom: 4px;
        margin-top: 18px;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .company-header {
        margin-top: 12px;
        margin-bottom: 6px;
    }
    .company-name {
        font-size: 12pt;
        font-weight: bold;
        color: #1a252f;
    }
    .company-desc {
        font-style: italic;
        color: #666666;
        font-size: 9.5pt;
        display: block;
        margin-top: 2px;
    }
    .role-header {
        margin-top: 8px;
        margin-bottom: 4px;
        clear: both;
    }
    .role-title {
        font-weight: bold;
        color: #34495e;
        font-size: 10.5pt;
    }
    .role-date {
        float: right;
        font-weight: bold;
        color: #2980b9;
        font-size: 10pt;
    }
    ul {
        margin-top: 4px;
        margin-bottom: 12px;
        padding-left: 18px;
    }
    li {
        margin-bottom: 5px;
        text-align: justify;
    }
    .skills-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 5px;
        margin-bottom: 15px;
    }
    .skills-table td {
        padding: 4px 0;
        vertical-align: top;
    }
    .skill-cat {
        font-weight: bold;
        width: 25%;
        color: #2c3e50;
    }
    .skill-list {
        width: 75%;
        color: #444444;
    }
    .early-career td {
        padding: 2px 0;
    }
</style>
</head>
<body>

<h1>[REDACTED] [REDACTED]</h1>
<div class="contact-info">
    [REDACTED_LOCATION], WA | [REDACTED_EMAIL] | [REDACTED_PHONE]
</div>

<div class="summary">
    Principal Software Engineer and Technical Architect specializing in highly scalable backend systems, complex data pipelines, and infrastructure optimization. Proven track record of driving business value through cross-functional collaboration, partnering directly with business departments to engineer solutions that optimize workflows, scale revenue, and generate massive cost savings. Led the foundational architecture from an early-stage startup to a successful exit.
</div>

<h2>Professional Experience</h2>

<div class="company-header">
    <span class="company-name">Whitepages</span>
    <span class="company-desc">A high-volume data platform serving identity verification, people search, and real estate products at scale.</span>
</div>

<div class="role-header">
    <span class="role-title">Principal Software Engineer, Data & Web</span>
    <span class="role-date">2020-2026</span>
</div>
<ul>
    <li>Spearheaded generative AI integration into core engineering workflows by driving the adoption and establishing organizational standards for AI coding using Claude Code, accelerating overall developer velocity</li>
    <li>Led the ground-up architecture and launch of a new consumer PropTech platform, integrating predictive machine learning models to generate automated, high-accuracy property valuations and rental income estimates at scale. As part of this initiative, led the implementation of Landon, the Whitepages AI real estate assistant using AWS Bedrock, RAG architecture and LLM integration</li>
    <li>Conceptualized and drove the implementation of a centralized internal platform that accelerated the marketing department's experimentation velocity by 3x, directly unlocking new company revenue streams and earning the CEO spot bonus for outstanding business impact</li>
    <li>Partnered with the marketing department to drive conversion rate optimization (CRO) across user-facing properties, championing strict architectural standards for Core Web Vitals and technical SEO that directly improved organic reach and user acquisition</li>
    <li>Fostered a culture of engineering excellence by mentoring cross-functional teams, leading technical training sessions, and establishing best practices for system architecture</li>
</ul>

<div class="role-header">
    <span class="role-title">Senior Software Engineer, Data</span>
    <span class="role-date">2019-2020</span>
</div>
<ul>
    <li>Rebuilt the core Whitepages data asset from scratch following a corporate spin-off, driving the implementation of a highly scalable data ingestion pipeline using Scala, Databricks, Elasticsearch and Prefect to power the company's central search product</li>
    <li>Spearheaded the search result optimization initiative across the organization</li>
    <li>Engineered six-figure cost savings in the backend systems by optimizing Elasticsearch infrastructure, allowing the company to use in-house solutions and bypass an expensive managed-hosting migration</li>
</ul>

<div class="company-header" style="page-break-before: avoid;">
    <span class="company-name">Contacts+ (acquired by FullContact)</span>
    <span class="company-desc">An industry-leading identity resolution platform and SaaS provider for professional contact management.</span>
</div>

<div class="role-header">
    <span class="role-title">Senior Backend Architect, FullContact</span>
    <span class="role-date">2018-2019</span>
</div>
<ul>
    <li>Directed the continued leadership of the Contacts+ backend and data asset development following the acquisition of Contacts+</li>
</ul>

<div class="role-header">
    <span class="role-title">Senior Software Architect, Contacts+</span>
    <span class="role-date">2012-2018</span>
</div>
<ul>
    <li>Employee #1 at an early-stage startup, driving the ground-up architecture of a highly scalable backend and proprietary data asset leveraging MongoDB and Redis, that grew to support hundreds of thousands of daily active users and culminated in a successful exit</li>
    <li>Architected and deployed a high-throughput Node.js API layer, alongside complex data aggregation pipelines designed to synthesize millions of records from various sources into a unified, clean data model</li>
    <li>Engineered the native contacts management client app for Android, applying deep systems knowledge to optimize performance, memory allocation, and battery lifecycle across Dalvik and ART runtimes</li>
</ul>

<h2>Early Career History</h2>
<table class="skills-table early-career">
    <tr><td class="skill-cat" style="width:15%">2007-2011</td><td class="skill-list">Software Developer, R&D Team Leader, ViGSM</td></tr>
    <tr><td class="skill-cat" style="width:15%">2006-2007</td><td class="skill-list">Software Developer, Atelis PLC</td></tr>
    <tr><td class="skill-cat" style="width:15%">2005-2006</td><td class="skill-list">Software Developer, Winbond</td></tr>
    <tr><td class="skill-cat" style="width:15%">2000-2004</td><td class="skill-list">Developer, KDE (Open Source Project)</td></tr>
</table>

<h2>Core Technologies & Architectures</h2>
<table class="skills-table">
    <tr><td class="skill-cat">Languages & Frameworks</td><td class="skill-list">Java, Scala, TypeScript, JavaScript, Python, C, C++, Perl, Shell Scripting</td></tr>
    <tr><td class="skill-cat">AI & Machine Learning</td><td class="skill-list">LLM Integration, RAG, AWS Bedrock, Claude Code, OpenRouter, OpenCode, Predictive ML Models</td></tr>
    <tr><td class="skill-cat">Cloud & Infrastructure</td><td class="skill-list">AWS (EC2, S3, Route 53, Lambda, IAM), Cloudflare (R2, Cloudflare Workers, WAF)</td></tr>
    <tr><td class="skill-cat">Databases & Data Stores</td><td class="skill-list">Elasticsearch/OpenSearch, MongoDB, DynamoDB, Redis/Valkey, PostgreSQL, MySQL</td></tr>
    <tr><td class="skill-cat">DevOps & Orchestration</td><td class="skill-list">Kubernetes, Docker, Terraform, Helm, Jenkins</td></tr>
</table>

<h2>Education</h2>
<div style="font-weight: bold; color: #2c3e50; font-size: 10.5pt; padding-bottom: 20px;">
    B.Sc., Computer Science, Tel Aviv University
</div>

</body>
</html>
"""

# Save to PDF
pdf_path = "[REDACTED]_[REDACTED]_Resume_Polished.pdf"
weasyprint.HTML(string=html_content).write_pdf(pdf_path)
print(f"Created {pdf_path}")

