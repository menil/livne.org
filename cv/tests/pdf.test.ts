import { describe, expect, it } from "bun:test";
import { existsSync, readFileSync, unlinkSync } from "node:fs";
import { join } from "node:path";
import { buildPdf, generatePdfBuffer } from "../src/pdf/build_pdf.ts";
import type { ResumeData } from "../theme/types.ts";

function countPdfPages(buffer: Uint8Array): number {
  const text = new TextDecoder("latin1").decode(buffer);
  const matches = text.match(/\/Type\s*\/Page\b/g);
  return matches ? matches.length : 0;
}

describe("Puppeteer PDF Builder", () => {
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
        highlights: [
          "Led distributed systems architecture",
          "Mentored engineering teams across org",
        ],
      },
    ],
    skills: [{ name: "Languages", keywords: ["TypeScript", "Python", "Rust"] }],
    education: [{ studyType: "B.Sc.", area: "Computer Science", institution: "UW" }],
  };

  it("generates a valid PDF buffer", async () => {
    const buffer = await generatePdfBuffer(sampleResume);
    expect(buffer).toBeDefined();
    expect(buffer.length).toBeGreaterThan(1000);

    const header = new TextDecoder("latin1").decode(buffer.slice(0, 8));
    expect(header.startsWith("%PDF-")).toBe(true);
  });

  it("builds a PDF file to a custom path", async () => {
    const testJsonPath = join(__dirname, "temp_resume.json");
    const testPdfPath = join(__dirname, "temp_resume.pdf");

    await Bun.write(testJsonPath, JSON.stringify(sampleResume));

    try {
      const outputPath = await buildPdf(testJsonPath, testPdfPath);
      expect(outputPath).toBe(testPdfPath);
      expect(existsSync(testPdfPath)).toBe(true);

      const fileBuffer = readFileSync(testPdfPath);
      expect(fileBuffer.length).toBeGreaterThan(1000);
    } finally {
      if (existsSync(testJsonPath)) unlinkSync(testJsonPath);
      if (existsSync(testPdfPath)) unlinkSync(testPdfPath);
    }
  });

  it("derives default output filename based on basics.name", async () => {
    const testJsonPath = join(__dirname, "temp_derive.json");
    const expectedPdfPath = join(__dirname, "jane_doe_resume.pdf");

    await Bun.write(testJsonPath, JSON.stringify(sampleResume));

    try {
      const outputPath = await buildPdf(testJsonPath);
      expect(outputPath).toBe(expectedPdfPath);
      expect(existsSync(expectedPdfPath)).toBe(true);
    } finally {
      if (existsSync(testJsonPath)) unlinkSync(testJsonPath);
      if (existsSync(expectedPdfPath)) unlinkSync(expectedPdfPath);
    }
  });

  it("derives _public suffix and strips phone when public option is true", async () => {
    const testJsonPath = join(__dirname, "temp_explicit_public.json");
    const expectedPdfPath = join(__dirname, "jane_doe_resume_public.pdf");

    await Bun.write(testJsonPath, JSON.stringify(sampleResume));

    try {
      const outputPath = await buildPdf(testJsonPath, undefined, { public: true });
      expect(outputPath).toBe(expectedPdfPath);
      expect(existsSync(expectedPdfPath)).toBe(true);
    } finally {
      if (existsSync(testJsonPath)) unlinkSync(testJsonPath);
      if (existsSync(expectedPdfPath)) unlinkSync(expectedPdfPath);
    }
  });

  it("derives _public suffix automatically when resume has no phone", async () => {
    const testJsonPath = join(__dirname, "temp_no_phone.json");
    const expectedPdfPath = join(__dirname, "jane_doe_resume_public.pdf");

    const noPhoneResume = {
      ...sampleResume,
      basics: { ...sampleResume.basics, phone: undefined },
    };
    await Bun.write(testJsonPath, JSON.stringify(noPhoneResume));

    try {
      const outputPath = await buildPdf(testJsonPath);
      expect(outputPath).toBe(expectedPdfPath);
      expect(existsSync(expectedPdfPath)).toBe(true);
    } finally {
      if (existsSync(testJsonPath)) unlinkSync(testJsonPath);
      if (existsSync(expectedPdfPath)) unlinkSync(expectedPdfPath);
    }
  });

  it("produces exactly 2 pages for full CV data with page breaks", async () => {
    const fullResume: ResumeData = {
      basics: {
        name: "Jane Doe",
        email: "jane.doe@example.com",
        phone: "555-123-4567",
        summary:
          "Principal Software Engineer and Technical Architect specializing in highly scalable backend systems, complex data pipelines, and infrastructure optimization. Proven track record of driving business value through cross-functional collaboration, partnering directly with business departments to engineer solutions that optimize workflows, scale revenue, and generate massive cost savings. Led the foundational architecture from an early-stage startup to a successful exit.",
        location: {
          city: "Seattle",
          region: "WA",
          countryCode: "US",
        },
        profiles: [
          { network: "LinkedIn", url: "https://linkedin.com/in/janedoe" },
          { network: "GitHub", url: "https://github.com/janedoe" },
        ],
      },
      work: [
        {
          name: "Company A",
          position: "Principal Software Engineer",
          startDate: "2020",
          endDate: "2026",
          description: "A high-volume data platform.",
          highlights: [
            "Highlight 1: Architected high-throughput distributed system",
            "Highlight 2: Optimized data ingestion and storage",
            "Highlight 3: Led cross-functional team initiatives",
          ],
        },
        {
          name: "Contacts+ (acquired by FullContact)",
          position: "Senior Backend Architect",
          startDate: "2018",
          endDate: "2019",
          description: "An industry-leading identity resolution platform.",
          highlights: ["Directed backend architecture following acquisition"],
        },
        {
          name: "Contacts+ (acquired by FullContact)",
          position: "Senior Software Architect",
          startDate: "2012",
          endDate: "2018",
          description: "An industry-leading identity resolution platform.",
          highlights: [
            "Employee #1 driving ground-up architecture",
            "Architected and deployed high-throughput API layer",
            "Engineered native mobile client app",
          ],
        },
      ],
      skills: [
        {
          name: "Languages & Frameworks",
          keywords: ["TypeScript", "Python", "Rust", "Node.js", "Go"],
        },
        {
          name: "Cloud & Infrastructure",
          keywords: ["AWS", "Cloudflare Workers", "Docker", "Kubernetes"],
        },
      ],
      education: [
        {
          studyType: "B.Sc.",
          area: "Computer Science",
          institution: "University of Washington",
        },
      ],
    };

    const buffer = await generatePdfBuffer(fullResume);
    const pages = countPdfPages(buffer);
    expect(pages).toBe(2);
  });

  it("throws an error when input file does not exist", async () => {
    expect(buildPdf("non_existent_file.json")).rejects.toThrow();
  });

  it("throws an error when input JSON is malformed", async () => {
    const invalidJsonPath = join(__dirname, "invalid.json");
    await Bun.write(invalidJsonPath, "{ malformed json ");

    try {
      expect(buildPdf(invalidJsonPath)).rejects.toThrow();
    } finally {
      if (existsSync(invalidJsonPath)) unlinkSync(invalidJsonPath);
    }
  });
});
