# Reference contract

Reference: [云PC软硬件检查报告.docx](../%E4%BA%91PC%E8%BD%AF%E7%A1%AC%E4%BB%B6%E6%A3%80%E6%9F%A5%E6%8A%A5%E5%91%8A.docx)
SHA256: fc206e63af54b37f193e7a92d31869354598059053167358798009ea561e1428
Reference render: `/tmp/dot-report-reference` (temporary local render, not included in this repository); 10 pages, all inspected. One portrait A4 section; all pages use the same body, table, and footer system. No figures or rich content controls need preservation.

Page: 21 × 29.7 cm; margins top/bottom 1.8 cm, left/right 2 cm; footer distance 0.8 cm. Preserve sectPr and style/numbering/theme parts byte-for-byte. Title 24 pt black, line 32 pt; body Noto Sans CJK SC 10 pt, exact line 15 pt, after 6 pt; Heading 1 17 pt/24 pt with page break before; Heading 2 12 pt/18 pt, before 9 pt. Footer right aligned date and PAGE field, 8 pt. Update date only. No title rules.

Tables: clone actual source table/row/cell properties. 17 cm total width, deliberately unequal columns; header E8EEF4, alternating F7F8FA/FFFFFF; D9D9D9 borders 4 eighth-points; 85 dxa padding; centered vertically; text 9 pt/13 pt, after 1 pt. Repeat headers; do not split individual rows. Table row count may change. No fixed heights. Source link style 245A81, after 4 pt.

Editable slots: word/document.xml body title, subtitle, metadata, executive paragraphs and table, numbered section blocks and references. All source-specific prose and tables are replaced; chapter/table patterns may repeat to accommodate Dot findings. word/footer1.xml date is editable; PAGE field preserved. core properties title/subject/date are editable. document relationships may add verified source hyperlinks and remove unused source hyperlinks. All other package parts and original relationships preserve-only. Heading section order follows summary, runtime, resources/storage, networking, software, capabilities, security, lifecycle/design, follow-up, evidence/references; extra scope section is allowed because this is a retrospective evidence review rather than a live inspection.

Build by cloning the reference ZIP, replacing body elements with source-derived paragraph/table prototypes, updating footer date, and adding source hyperlink relations. Keep complete reference untouched. The report must label record-only claims and distinguish original commands from assistant narrative. Final render must inspect every page and verify section geometry, source links, preserve-only hashes, and reference hash. More pages than source are expected because source provenance is expanded. No claims are invented to fill slots.

Field handling: word/settings.xml is additionally editable only to set updateFields=true because native Word refresh is unavailable. PAGE fields remain intact and render to the current 12-page pagination. All other settings retain their XML semantics.
