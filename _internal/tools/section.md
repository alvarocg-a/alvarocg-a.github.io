# Tools

## Section intro

Unreal Engine plugins I design and publish on Fab: drop-in C++ systems for navigation and UI that work in
an existing project without changing its classes, and come out again cleanly. Every claim on their store
pages is backed by a test or a benchmark that ships with the plugin.

## Order

1. `minimap-full-map-system`
2. `screen-waypoint-markers`

## Featured on the portfolio home

`minimap-full-map-system`, because it has the strongest story: a saturated category, a position chosen
from research, and a performance claim proven by a benchmark that ships with the plugin.

## Notes for the portfolio build

- Both listings are live on Fab (Screen Waypoint Markers since 7 Oct 2026, Minimap & Full Map System
  since 11 Oct 2026). The Fab links in each `tool.md` are the public listing pages.
- No video for either tool: `video` is empty on purpose. Use the cover image as the main image.
- **Documentation:** each tool folder has a `docs/` copy of what ships inside the plugin: the user guide
  (PDF, the `docs_url` target) and the technical README (`README.md`, setup, every setting and the
  Blueprint / C++ API). Host them with the tool page; the secondary "Documentation" button can point to
  the PDF.
- All images are 1920x1080 PNG captures from the demo maps, except `minimap-full-map-system/04.png`,
  a chart generated from the benchmark data.
- The demo maps carry big in-world signage ("ACGA WAYPOINT DEMO…") that shows in some captures; it is
  the demo's own text, not UI.

## Use of AI (for the site builder to decide)

Both plugins were built with generative AI as a coding assistant for the C++ source and the
documentation. No AI-generated art, audio or media. This is declared on both Fab listings ("generative
AI used: yes"), so anything the portfolio says should not contradict it.

Whether and how to mention it on the site is the site builder's call. If it is mentioned, the accurate
wording is the one above: AI as a coding and documentation assistant, with the design, the decisions,
the research, the playtests and the publishing done by Álvaro.
