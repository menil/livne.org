import type Handlebars from "handlebars";
import type {
  Basics,
  CompanyGroup,
  PreparedResume,
  ResumeData,
  WorkEntry,
  WorkRole,
} from "./types.ts";

export const EARLY_CAREER_YEARS = 10;

export function getProfile(basics?: Basics, networkName?: string): string {
  if (!basics?.profiles || !networkName) return "";
  const target = networkName.toLowerCase();
  for (const profile of basics.profiles) {
    if (profile.network?.toLowerCase() === target) {
      return profile.url || "";
    }
  }
  return "";
}

export function getLinkedIn(basics?: Basics): string {
  return getProfile(basics, "linkedin");
}

export function getGitHub(basics?: Basics): string {
  return getProfile(basics, "github");
}

export function getEndYear(entry: WorkRole): number | null {
  if (!entry.endDate) return null;
  const yearStr = entry.endDate.toString().slice(0, 4);
  const year = Number.parseInt(yearStr, 10);
  return Number.isNaN(year) ? null : year;
}

export function formatDates(start?: string, end?: string): string {
  if (start && end) return `${start}-${end}`;
  if (end) return end;
  if (start) return `${start}-Present`;
  return "";
}

export function groupWork(work?: WorkEntry[]): CompanyGroup[] {
  if (!work || work.length === 0) return [];
  const groups: CompanyGroup[] = [];

  for (const entry of work) {
    const role: WorkRole = {
      position: entry.position || "",
      startDate: entry.startDate,
      endDate: entry.endDate,
      highlights: entry.highlights || [],
      summary: entry.summary,
      dates: formatDates(entry.startDate, entry.endDate),
    };

    if (groups.length > 0 && groups[groups.length - 1].name === entry.name) {
      groups[groups.length - 1].roles.push(role);
    } else {
      groups.push({
        name: entry.name,
        description: entry.description || "",
        roles: [role],
      });
    }
  }

  return groups;
}

export function prepareResume(data: ResumeData, asOfYear?: number): PreparedResume {
  const currentYear = asOfYear ?? new Date().getFullYear();
  const thresholdYear = currentYear - EARLY_CAREER_YEARS;

  const companies: CompanyGroup[] = [];
  const earlyCareerCompanies: CompanyGroup[] = [];

  const grouped = groupWork(data.work);
  for (const group of grouped) {
    const endYears = group.roles.map((r) => getEndYear(r));
    const isEarly =
      endYears.length > 0 && endYears.every((year) => year !== null && year < thresholdYear);

    if (isEarly) {
      earlyCareerCompanies.push(group);
    } else {
      companies.push(group);
    }
  }

  const slug = (data.basics?.name || "cv").toLowerCase().replace(/\s+/g, "_");
  const pdfUrl = `${slug}_resume.pdf`;

  const basics: Basics = {
    ...(data.basics || {}),
    linkedin: getLinkedIn(data.basics),
    github: getGitHub(data.basics),
    pdf_url: pdfUrl,
  };

  const earlyCareer = earlyCareerCompanies.flatMap((company) =>
    company.roles.map((role) => ({
      dates: role.dates || "",
      details: `${role.position}, ${company.name}`,
    })),
  );

  return {
    basics,
    work: companies,
    early_career: earlyCareer,
    skills: data.skills || [],
    education: data.education || [],
  };
}

export function stripUrl(url?: string): string {
  if (!url) return "";
  return url.replace(/^https?:\/\//, "").replace(/^www\./, "");
}

export function registerHelpers(hbs: typeof Handlebars): void {
  hbs.registerHelper("formatDates", formatDates);
  hbs.registerHelper("stripUrl", stripUrl);
  hbs.registerHelper("join", (arr: unknown[], sep: string) =>
    Array.isArray(arr) ? arr.join(sep) : "",
  );
  hbs.registerHelper("eq", (a: unknown, b: unknown) => a === b);
  hbs.registerHelper("contains", (str: string, substr: string) =>
    typeof str === "string" && typeof substr === "string" ? str.includes(substr) : false,
  );
}
