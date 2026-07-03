---
type: resolver
---

# summaries/

One distilled summary per ingested source — articles, papers, transcripts, videos, books.

## What goes here

- Distilled article or blog post summaries
- Book notes (one file per book)
- Transcript distillations (when the primary value is the content, not the event)
- Research paper summaries
- Video/podcast notes

## What does NOT go here

- Meeting summaries or call recaps → those are dated events, they go in `journal/`
- Analysis of a specific person → update `people/` instead
- Analysis of a specific venture → update `ventures/` instead
- Raw source documents (unmodified) → those go in `raw/`

## One file per source

Each summary file corresponds to exactly one source document. If you're distilling multiple sources on a topic into one synthesis, that's a `knowledge/` page, not a summary.

## Format

```markdown
---
date: YYYY-MM-DD
type: summary
source: <URL or path to raw source>
tags: [...]
---

# Source Title

> One-line takeaway.

## Key Points
- ...

## Quotes
> "..." — Author

## Implications / How This Applies
...
```

## See also

- [[_system/conventions/filing-rules]] — journal vs. summary distinction
- [[_system/conventions/source-attribution]] — cite the source in the frontmatter
