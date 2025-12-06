# Research for: Humanoid Robotics AI Book

This document outlines the key technology and platform decisions for the project. All choices were derived directly from the project constitution and feature specification.

## 1. Content and Build Engine

-   **Decision**: Docusaurus v3
-   **Rationale**: The project requires a static site generator optimized for documentation with Markdown, React components, and sidebar navigation. Docusaurus is the industry standard for this and was specified in the project requirements. It directly supports deployment to GitHub Pages.
-   **Alternatives Considered**:
    -   **Jekyll/Hugo**: While powerful, they are not React-based, which limits the ability to create custom interactive components. Docusaurus's architecture is a better fit.
    -   **VitePress**: A strong contender, but Docusaurus has a more extensive ecosystem and plugin library for documentation-specific features.

## 2. Development Workflow and Tooling

-   **Decision**: Spec-Kit Plus & Claude Code
-   **Rationale**: The project constitution mandates a Spec-Driven workflow and the use of a specific AI agent for content generation. This tooling is a hard constraint.
-   **Alternatives Considered**: None, as this was a primary project constraint.

## 3. Visualizations

-   **Decision**: Mermaid.js and ASCII Diagrams
-   **Rationale**: The constitution requires diagrams that are reproducible and Markdown-safe. Docusaurus has built-in support for Mermaid.js, and ASCII diagrams are universally compatible. This approach avoids the need for binary image assets, keeping the repository lightweight and text-based.
-   **Alternatives Considered**:
    -   **PNG/JPG Images**: Rejected because they are not text-based, harder to version control, and require external tools to create and edit.

## Conclusion

The technical stack is confirmed. No outstanding research questions remain.
