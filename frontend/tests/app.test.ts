import { describe, it, expect } from "vitest";

describe("Interngram frontend", () => {
  it("API URL defaults correctly", () => {
    const url = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    expect(url).toContain("/api/v1");
  });
});
