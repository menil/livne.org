import { describe, expect, it } from "bun:test";
import Handlebars from "handlebars";
import {
  EARLY_CAREER_YEARS,
  formatDates,
  getEndYear,
  getGitHub,
  getLinkedIn,
  getProfile,
  groupWork,
  prepareResume,
  registerHelpers,
  stripUrl,
} from "../theme/helpers.ts";
import type { ResumeData } from "../theme/types.ts";

describe("Handlebars & Theme Helpers", () => {
  describe("getProfile, getLinkedIn & getGitHub", () => {
    it("extracts arbitrary profile URL (case-insensitive)", () => {
      const basics = {
        profiles: [
          { network: "Twitter", url: "https://twitter.com/janedoe" },
          { network: "LinkedIn", url: "https://linkedin.com/in/janedoe" },
          { network: "GitHub", url: "https://github.com/janedoe" },
        ],
      };
      expect(getProfile(basics, "twitter")).toBe("https://twitter.com/janedoe");
      expect(getProfile(basics, "TWITTER")).toBe("https://twitter.com/janedoe");
      expect(getProfile(basics, "nonexistent")).toBe("");
      expect(getProfile(undefined, "twitter")).toBe("");
      expect(getProfile(basics, undefined)).toBe("");
    });

    it("extracts LinkedIn profile URL (case-insensitive)", () => {
      expect(
        getLinkedIn({
          profiles: [
            { network: "Twitter", url: "https://twitter.com/janedoe" },
            { network: "LinkedIn", url: "https://linkedin.com/in/janedoe" },
          ],
        }),
      ).toBe("https://linkedin.com/in/janedoe");
    });

    it("returns empty string if LinkedIn profile is not present", () => {
      expect(getLinkedIn({ profiles: [] })).toBe("");
      expect(getLinkedIn({})).toBe("");
      expect(getLinkedIn(undefined)).toBe("");
    });

    it("extracts GitHub profile URL (case-insensitive)", () => {
      expect(
        getGitHub({
          profiles: [{ network: "GITHUB", url: "https://github.com/janedoe" }],
        }),
      ).toBe("https://github.com/janedoe");
    });

    it("returns empty string if GitHub profile is not present", () => {
      expect(getGitHub({ profiles: [] })).toBe("");
      expect(getGitHub({})).toBe("");
    });
  });

  describe("getEndYear", () => {
    it("extracts 4-digit start year", () => {
      expect(getEndYear({ endDate: "2024" })).toBe(2024);
      expect(getEndYear({ endDate: "2020-05" })).toBe(2020);
      expect(getEndYear({ endDate: "2018-06-15" })).toBe(2018);
    });

    it("returns null for missing or invalid dates", () => {
      expect(getEndYear({})).toBeNull();
      expect(getEndYear({ endDate: "invalid" })).toBeNull();
    });
  });

  describe("formatDates", () => {
    it("formats start and end", () => {
      expect(formatDates("2020", "2026")).toBe("2020-2026");
    });

    it("formats end only", () => {
      expect(formatDates(undefined, "2020")).toBe("2020");
    });

    it("formats start only as Present", () => {
      expect(formatDates("2020", undefined)).toBe("2020-Present");
    });

    it("returns empty string for empty inputs", () => {
      expect(formatDates(undefined, undefined)).toBe("");
      expect(formatDates("", "")).toBe("");
    });
  });

  describe("groupWork", () => {
    it("returns empty array for empty work", () => {
      expect(groupWork(undefined)).toEqual([]);
      expect(groupWork([])).toEqual([]);
    });

    it("groups consecutive roles under same company", () => {
      const work = [
        {
          name: "Acme Corp",
          position: "Staff Engineer",
          startDate: "2022",
          endDate: "2026",
          highlights: ["Project Alpha"],
        },
        {
          name: "Acme Corp",
          position: "Senior Engineer",
          startDate: "2020",
          endDate: "2022",
          highlights: ["Project Beta"],
        },
        {
          name: "Other Inc",
          position: "Architect",
          startDate: "2018",
          endDate: "2020",
        },
      ];

      const grouped = groupWork(work);
      expect(grouped).toHaveLength(2);
      expect(grouped[0].name).toBe("Acme Corp");
      expect(grouped[0].roles).toHaveLength(2);
      expect(grouped[0].roles[0].position).toBe("Staff Engineer");
      expect(grouped[0].roles[1].position).toBe("Senior Engineer");
      expect(grouped[1].name).toBe("Other Inc");
      expect(grouped[1].roles).toHaveLength(1);
    });
  });

  describe("prepareResume", () => {
    it("partitions early career (>10 years) and formats basics", () => {
      const sample: ResumeData = {
        basics: {
          name: "Jane Doe",
          profiles: [
            { network: "LinkedIn", url: "https://linkedin.com/in/janedoe" },
            { network: "GitHub", url: "https://github.com/janedoe" },
          ],
        },
        work: [
          {
            name: "Recent Corp",
            position: "Lead",
            startDate: "2022",
            endDate: "2026",
          },
          {
            name: "Old Startup",
            position: "Junior Dev",
            startDate: "2010",
            endDate: "2014",
          },
        ],
        skills: [{ name: "TypeScript", keywords: ["Bun", "Node"] }],
        education: [{ studyType: "B.Sc.", area: "Computer Science", institution: "Univ" }],
      };

      const prepared = prepareResume(sample, 2026);
      expect(prepared.basics.name).toBe("Jane Doe");
      expect(prepared.basics.linkedin).toBe("https://linkedin.com/in/janedoe");
      expect(prepared.basics.github).toBe("https://github.com/janedoe");
      expect(prepared.work).toHaveLength(1);
      expect(prepared.work[0].name).toBe("Recent Corp");
      expect(prepared.early_career).toHaveLength(1);
      expect(prepared.early_career[0]).toEqual({
        dates: "2010-2014",
        details: "Junior Dev, Old Startup",
      });
      expect(prepared.skills).toHaveLength(1);
      expect(prepared.education).toHaveLength(1);
    });

    it("does not classify active/open-ended role as early career", () => {
      const sample: ResumeData = {
        work: [
          {
            name: "Long Term Corp",
            position: "Founder",
            startDate: "2010",
          },
        ],
      };

      const prepared = prepareResume(sample, 2026);
      expect(prepared.work).toHaveLength(1);
      expect(prepared.early_career).toHaveLength(0);
    });
  });

  describe("stripUrl", () => {
    it("strips http://, https://, and www.", () => {
      expect(stripUrl("https://www.linkedin.com/in/janedoe")).toBe("linkedin.com/in/janedoe");
      expect(stripUrl("http://github.com/janedoe")).toBe("github.com/janedoe");
      expect(stripUrl("")).toBe("");
      expect(stripUrl(undefined)).toBe("");
    });
  });

  describe("registerHelpers", () => {
    it("registers helpers and evaluates templates correctly", () => {
      const hbs = Handlebars.create();
      registerHelpers(hbs);

      const template = hbs.compile(
        "{{stripUrl url}} | {{join keywords ', '}} | {{#if (eq name 'Jane')}}Yes{{/if}} | {{#if (contains summary 'Lead')}}Match{{/if}}",
      );

      const result = template({
        url: "https://example.com/test",
        keywords: ["TS", "Bun", "Rust"],
        name: "Jane",
        summary: "Tech Lead at Company",
      });

      expect(result).toBe("example.com/test | TS, Bun, Rust | Yes | Match");
    });
  });
});
