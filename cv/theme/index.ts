import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import Handlebars from "handlebars";
import { prepareResume, registerHelpers } from "./helpers.ts";
import type { ResumeData, ThemeOptions } from "./types.ts";

const currentDir =
  typeof __dirname !== "undefined" ? __dirname : dirname(new URL(import.meta.url).pathname);

const templateSource = readFileSync(join(currentDir, "template.hbs"), "utf-8");
const styleCss = readFileSync(join(currentDir, "style.css"), "utf-8");

const hbs = Handlebars.create();
registerHelpers(hbs);
hbs.registerHelper("or", (...args: unknown[]) => {
  // Last argument is handlebars options object
  const items = args.slice(0, -1);
  return items.some((item) => Boolean(item));
});
hbs.registerHelper("and", (...args: unknown[]) => {
  const items = args.slice(0, -1);
  return items.every((item) => Boolean(item));
});

const compiledTemplate = hbs.compile(templateSource);

export function render(resume: ResumeData = {}, options: ThemeOptions = {}): string {
  const prepared = prepareResume(resume, options.asOfYear);
  prepared.is_pdf = options.is_pdf ?? false;

  return compiledTemplate({
    ...prepared,
    css: styleCss,
  });
}

/**
 * Builds an HTML file from a JSON Resume file.
 */
export function buildHtml(
  inputJsonPath: string,
  outputPath?: string,
  options: ThemeOptions = {},
): string {
  const raw = readFileSync(inputJsonPath, "utf-8");
  const data: ResumeData = JSON.parse(raw);

  let targetPath = outputPath;
  if (!targetPath) {
    const name = data.basics?.name || "resume";
    // Replace non-alphanumeric characters (except hyphen and underscore) with underscore for safe filename generation
    const slug = name.toLowerCase().replace(/[^a-z0-9_-]+/g, "_");
    targetPath = join(dirname(inputJsonPath), `${slug}_resume.html`);
  }

  mkdirSync(dirname(targetPath), { recursive: true });
  const html = render(data, options);
  writeFileSync(targetPath, html, "utf-8");
  return targetPath;
}

// CLI usage: bun theme/index.ts <input.json> [output.html]
const isCliEntrypoint =
  typeof process !== "undefined" &&
  process.argv[1] !== undefined &&
  fileURLToPath(import.meta.url) === process.argv[1];

if (isCliEntrypoint) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error("Usage: bun theme/index.ts <input.json> [output.html]");
    process.exit(1);
  }

  const inputFile = args[0];
  const outputFile = args[1];

  try {
    const createdPath = buildHtml(inputFile, outputFile);
    console.log(`Success! Created ${createdPath}`);
  } catch (err) {
    console.error("Error generating HTML:", err);
    process.exit(1);
  }
}
