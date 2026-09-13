export interface Profile {
  network?: string;
  username?: string;
  url?: string;
}

export interface Location {
  address?: string;
  postalCode?: string;
  city?: string;
  countryCode?: string;
  region?: string;
}

export interface Basics {
  name?: string;
  label?: string;
  image?: string;
  email?: string;
  phone?: string;
  url?: string;
  summary?: string;
  location?: Location;
  profiles?: Profile[];
  linkedin?: string;
  github?: string;
  pdf_url?: string;
}

export interface WorkRole {
  position?: string;
  startDate?: string;
  endDate?: string;
  highlights?: string[];
  summary?: string;
  dates?: string;
}

export interface WorkEntry extends WorkRole {
  name: string;
  description?: string;
  url?: string;
}

export interface CompanyGroup {
  name: string;
  description?: string;
  roles: WorkRole[];
}

export interface EarlyCareerEntry {
  dates: string;
  details: string;
}

export interface Skill {
  name?: string;
  level?: string;
  keywords?: string[];
}

export interface Education {
  institution?: string;
  url?: string;
  area?: string;
  studyType?: string;
  startDate?: string;
  endDate?: string;
  score?: string;
  courses?: string[];
}

export interface ResumeData {
  basics?: Basics;
  work?: WorkEntry[];
  skills?: Skill[];
  education?: Education[];
  [key: string]: unknown;
}

export interface PreparedResume {
  basics: Basics;
  work: CompanyGroup[];
  early_career: EarlyCareerEntry[];
  skills: Skill[];
  education: Education[];
  is_pdf?: boolean;
}

export interface ThemeOptions {
  is_pdf?: boolean;
  asOfYear?: number;
}
