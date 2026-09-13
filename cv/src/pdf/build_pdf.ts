#!/usr/bin/env bun
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import puppeteer from "puppeteer";
import { render } from "../../theme/index.ts";
import type { ResumeData, ThemeOptions } from "../../theme/types.ts";

export interface BuildPdfOptions extends ThemeOptions {
  outputPath?: string;
  public?: boolean;
}

/**
 * Renders resume data to an HTML string using the theme and prints to a PDF buffer via Puppeteer.
 */
export async function generatePdfBuffer(
  resume: ResumeData,
  options: BuildPdfOptions = {},
): Promise<Uint8Array> {
  const resumeData = structuredClone(resume);
  if (options.public && resumeData.basics) {
    delete resumeData.basics.phone;
  }

  const html = render(resumeData, { ...options, is_pdf: true });

  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: "domcontentloaded" });
    await page.emulateMediaType("print");
    const pdf = await page.pdf({
      format: "Letter",
      printBackground: true,
      preferCSSPageSize: true,
    });
    return pdf;
  } finally {
    await browser.close();
  }
}

/**
 * Builds a PDF file from a JSON Resume file.
 */
export async function buildPdf(
  inputJsonPath: string,
  outputPath?: string,
  options: BuildPdfOptions = {},
): Promise<string> {
  const raw = readFileSync(inputJsonPath, "utf-8");
  const data: ResumeData = JSON.parse(raw);

  const isPublic = options.public ?? !data.basics?.phone;

  let targetPath = outputPath;
  if (!targetPath) {
    const name = data.basics?.name || "resume";
    const slug = name.toLowerCase().replace(/[^a-z0-9_-]+/g, "_");
    const filename = `${slug}_resume${isPublic ? "_public" : ""}.pdf`;
    targetPath = join(dirname(inputJsonPath), filename);
  }

  mkdirSync(dirname(targetPath), { recursive: true });
  const pdfBuffer = await generatePdfBuffer(data, { ...options, public: isPublic });
  writeFileSync(targetPath, pdfBuffer);
  return targetPath;
}

if (import.meta.main) {
  const isPublic = process.argv.includes("--public");
  const posArgs = process.argv.slice(2).filter((arg) => arg !== "--public");

  if (posArgs.length === 0) {
    console.error("Usage: bun src/pdf/build_pdf.ts [--public] <input.json> [output.pdf]");
    process.exit(1);
  }

  const inputJson = posArgs[0];
  const outputPdf = posArgs[1];

  buildPdf(inputJson, outputPdf, { public: isPublic || undefined })
    .then((createdPath) => {
      console.log(`Success! Created ${createdPath}`);
    })
    .catch((err) => {
      console.error("Error generating PDF:", err);
      process.exit(1);
    });
}
