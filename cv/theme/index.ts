import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
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

// CLI usage: bun theme/index.ts <input.json> [output.html]
if (import.meta.main) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error("Usage: bun theme/index.ts <input.json> [output.html]");
    process.exit(1);
  }

  const inputFile = args[0];
  const outputFile = args[1];

  const rawJson = readFileSync(inputFile, "utf-8");
  const data = JSON.parse(rawJson);
  const html = render(data);

  if (outputFile) {
    const { writeFileSync, mkdirSync } = require("node:fs");
    const { dirname } = require("node:path");
    mkdirSync(dirname(outputFile), { recursive: true });
    writeFileSync(outputFile, html, "utf-8");
    console.log(`Generated HTML resume: ${outputFile}`);
  } else {
    process.stdout.write(html);
  }
}
