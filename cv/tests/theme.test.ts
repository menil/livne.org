import { describe, expect, it } from "bun:test";
import { render } from "../theme/index.ts";

describe("theme", () => {
  it("renders empty string placeholder", () => {
    expect(render()).toBe("");
  });
});
