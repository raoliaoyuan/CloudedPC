# Illustration update contract

Task date: 2026-11-15 Asia/Singapore. Update the Dot audit, not the separate comparison report. Retain original text and tables; add eight source-labelled logical diagrams, PNG inline display, standalone SVG and native editable draw.io, and a multi-page draw.io collection. Also update Word and package the deliverables with portable relative asset links.

Content baseline: report-before-diagrams-2026-11-15.md and .docx in this directory. Keep these byte-for-byte. Visual authority for Word is this retained Dot DOCX and the existing ../artifact.md. Figure authority is the November 15 SVG/PNG/draw.io set in audit-2026-11-10/assets/report-diagrams. Use the shared blue/teal/amber palette and editable rounded boxes, connector arrows and typography. Increase diagram text sizes for legibility at 17 cm in Word.

Evidence boundary: original observations Nov 11 and official-document review Nov 13 remain unchanged. Nov 15 is a figure-update date, not a new remote measurement. Blue denotes reported historical values, teal official or expressly labelled user-confirmed capability, amber dashed items unknown or conditional. Solid arrows are source-labelled logical relationships, not proof of packet capture or physical deployment. Do not transplant Tencent Cloud, Docker, Supervisor, namespace, SSH, or log-agent facts into Dot diagrams. Where Dot evidence is missing, show that gap. Do not invent hardware or GUI design motives.

Word preservation: insert inline PNG figure pages at the end of chapters 1, 2, 3, 4, 6, 7 and two at chapter 8; retain all original paragraphs/tables and source hyperlinks. Add captions, source references and relative asset hyperlinks. One A4 section, original margins/fonts/tables preserved. Editable parts: document.xml, its relationships, content types, footer date and new media. Preserve all other parts byte-for-byte. PAGE field remains; updateFields already true. Add a figure-update notice after original date metadata.

Validation: inspect all SVG-derived PNGs, export all eight draw.io pages to verify genuine editability and inspect those renders, confirm node/edge references and no embedded raster image in SVG/draw.io. Render Word and inspect every final page. Check original prose/table preservation, source links, all relative package assets, source hashes, and ZIP integrity. Keep QA separate from deliverables.


## Final QA — 2026-11-15

- Inspected every page of the final 20-page Word render, all eight SVG-derived previews, and all eight native draw.io exports. No clipping, overlaps, missing glyphs or orphaned figure captions observed.
- Final comparison render and the first successful final render are pixel-identical on all 20 pages.
- Preserved all 140 original body elements, nine tables, original source references and pre-existing relationships; original styles and numbering parts remain unchanged.
- All 58 relative figure/attachment links resolve; complete package has 28 files and passes CRC and byte-for-byte content validation.
- Validation results: final-validation.json. Delivery: updated DOCX, Markdown, source index, eight PNG/SVG/draw.io sets, one eight-page draw.io file, complete ZIP. QA renders and source-evidence backups are excluded from the delivery ZIP.
