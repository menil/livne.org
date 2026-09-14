import { afterAll, beforeAll, describe, expect, it } from "bun:test";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

describe("Resumed CLI Pipeline", () => {
  let tmpDir: string;
  const sampleResume = {
    basics: {
      name: "Jane Doe",
      email: "jane.doe@example.com",
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
        highlights: [
          "Led distributed systems architecture",
          "Mentored engineering teams across org",
        ],
      },
    ],
    skills: [{ name: "Languages", keywords: ["TypeScript", "Python", "Rust"] }],
    education: [{ studyType: "B.Sc.", area: "Computer Science", institution: "UW" }],
  };

  beforeAll(() => {
    tmpDir = mkdtempSync(join(tmpdir(), "resumed-livne-test-"));
  });

  afterAll(() => {
    if (existsSync(tmpDir)) {
      rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it("renders HTML resume with resumed CLI", async () => {
    const inputJson = join(tmpDir, "resume.json");
    const outputHtml = join(tmpDir, "resume.html");

    await Bun.write(inputJson, JSON.stringify(sampleResume));

    const proc = Bun.spawnSync([
      "bun",
      "run",
      "--bun",
      "resumed",
      "render",
      inputJson,
      "-o",
      outputHtml,
      "-t",
      "jsonresume-theme-signal",
    ]);

    expect(proc.exitCode).toBe(0);
    expect(existsSync(outputHtml)).toBe(true);

    const content = readFileSync(outputHtml, "utf-8");
    expect(content).toContain("Jane Doe");
    expect(content).toContain("Principal Architect");
    expect(content).toContain("Tech Corp");
  });

  it("exports PDF resume with resumed CLI", async () => {
    const inputJson = join(tmpDir, "resume.json");
    const outputPdf = join(tmpDir, "resume.pdf");

    await Bun.write(inputJson, JSON.stringify(sampleResume));

    const proc = Bun.spawnSync([
      "bun",
      "run",
      "--bun",
      "resumed",
      "export",
      inputJson,
      "-o",
      outputPdf,
      "-t",
      "jsonresume-theme-signal",
      "--puppeteer-arg=--no-sandbox",
      "--puppeteer-arg=--disable-setuid-sandbox",
    ]);

    expect(proc.exitCode).toBe(0);
    expect(existsSync(outputPdf)).toBe(true);

    const fileBuffer = readFileSync(outputPdf);
    expect(fileBuffer.length).toBeGreaterThan(1000);
    const header = new TextDecoder("latin1").decode(fileBuffer.slice(0, 8));
    expect(header.startsWith("%PDF-")).toBe(true);
  });
});
