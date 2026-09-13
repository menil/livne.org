import { describe, expect, it } from "bun:test";
import { render } from "../theme/index.ts";
import type { ResumeData } from "../theme/types.ts";

describe("JSON Resume Theme Render", () => {
  const sampleResume: ResumeData = {
    basics: {
      name: "Jane Doe",
      email: "jane.doe@example.com",
      phone: "555-123-4567",
      summary: "Principal Architect specializing in scalable backend systems.",
      location: {
        city: "Seattle",
        region: "WA",
      },
      profiles: [
        { network: "LinkedIn", url: "https://linkedin.com/in/janedoe" },
        { network: "GitHub", url: "https://github.com/janedoe" },
      ],
    },
    work: [
      {
        name: "Tech Corp",
        position: "Principal Engineer",
        startDate: "2020",
        endDate: "2026",
        description: "High volume data platform.",
        highlights: ["Led distributed systems architecture", "Mentored engineering teams"],
      },
    ],
    skills: [{ name: "Languages", keywords: ["TypeScript", "Python", "Rust"] }],
    education: [{ studyType: "B.Sc.", area: "Computer Science", institution: "UW" }],
  };

  it("renders web HTML with action links and clean header", () => {
    const html = render(sampleResume);

    expect(html).toContain("<!DOCTYPE html>");
    expect(html).toContain("Jane Doe");
    expect(html).toContain("Seattle, WA");
    expect(html).toContain("jane.doe@example.com");
    expect(html).toContain("https://linkedin.com/in/janedoe");
    expect(html).toContain("https://github.com/janedoe");
    expect(html).toContain("jane_doe_resume.pdf");
    expect(html).toContain("Tech Corp");
    expect(html).toContain("Principal Engineer");
    expect(html).toContain("Led distributed systems architecture");
    expect(html).toContain("TypeScript, Python, Rust");
    expect(html).toContain("B.Sc., Computer Science");
  });

  it("renders PDF mode with textual phone and linkedin in header", () => {
    const html = render(sampleResume, { is_pdf: true });

    expect(html).toContain("555-123-4567");
    expect(html).toContain("linkedin.com/in/janedoe");
    expect(html).not.toContain('class="action-links"');
  });

  it("respects asOfYear option for early career partitioning", () => {
    const resumeWithOldJob: ResumeData = {
      ...sampleResume,
      work: [
        {
          name: "Old Corp",
          position: "Developer",
          startDate: "2010",
          endDate: "2014",
        },
      ],
    };
    const html2026 = render(resumeWithOldJob, { asOfYear: 2026 });
    expect(html2026).toContain("Early Career History");
    expect(html2026).toContain("Developer, Old Corp");

    const html2015 = render(resumeWithOldJob, { asOfYear: 2015 });
    expect(html2015).toContain("Professional Experience");
    expect(html2015).not.toContain("Early Career History");
  });

  it("handles empty resume gracefully", () => {
    const html = render({});
    expect(html).toContain("<!DOCTYPE html>");
    expect(html).toContain("<title>Resume</title>");
  });
});
