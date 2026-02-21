import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Badge } from "../Badge";

describe("Badge", () => {
  it("renders children text", () => {
    render(<Badge>Common</Badge>);
    expect(screen.getByText("Common")).toBeInTheDocument();
  });

  it("applies default color when no color prop", () => {
    render(<Badge>Default</Badge>);
    expect(screen.getByText("Default").className).toContain("bg-surface-3");
  });

  it("applies gold color class", () => {
    render(<Badge color="gold">Gold item</Badge>);
    expect(screen.getByText("Gold item").className).toContain("text-amber-300");
  });

  it("applies danger color class", () => {
    render(<Badge color="danger">Warning</Badge>);
    expect(screen.getByText("Warning").className).toContain("text-red-300");
  });

  it("renders icon alongside text", () => {
    render(<Badge icon={<span data-testid="icon">★</span>}>Starred</Badge>);
    expect(screen.getByTestId("icon")).toBeInTheDocument();
    expect(screen.getByText("Starred")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(<Badge className="mt-2">Custom</Badge>);
    expect(screen.getByText("Custom").className).toContain("mt-2");
  });

  it("applies tactical role colors", () => {
    render(<Badge color="brute">Brute</Badge>);
    expect(screen.getByText("Brute").className).toContain("text-red-300");
  });
});
