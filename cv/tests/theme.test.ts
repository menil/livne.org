import { describe, expect, it } from "bun:test";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { buildHtml, render } from "../theme/index.ts";
import type { ResumeData } from "../theme/types.ts";

const SAMPLE_RESUME: ResumeData = {
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

describe("JSON Resume Theme Render", () => {
  it("renders web HTML with action links and clean header", () => {
    const html = render(SAMPLE_RESUME);

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
    const html = render(SAMPLE_RESUME, { is_pdf: true });

    expect(html).toContain("555-123-4567");
    expect(html).toContain("linkedin.com/in/janedoe");
    expect(html).not.toContain('class="action-links"');
  });

  it("respects asOfYear option for early career partitioning", () => {
    const resumeWithOldJob: ResumeData = {
      ...SAMPLE_RESUME,
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

  it("builds an HTML file from JSON Resume", () => {
    const tmpDir = mkdtempSync(join(tmpdir(), "theme-test-"));
    const inputPath = join(tmpDir, "resume.json");
    Bun.write(inputPath, JSON.stringify(SAMPLE_RESUME));

    const outputPath = join(tmpDir, "custom.html");
    const result = buildHtml(inputPath, outputPath);
    expect(result).toBe(outputPath);
    expect(existsSync(outputPath)).toBeTrue();

    const content = readFileSync(outputPath, "utf-8");
    expect(content).toContain("Jane Doe");

    // Test default output path derivation
    const defaultResult = buildHtml(inputPath);
    expect(defaultResult).toBe(join(tmpDir, "jane_doe_resume.html"));
    expect(existsSync(defaultResult)).toBeTrue();

    rmSync(tmpDir, { recursive: true, force: true });
  });
});
