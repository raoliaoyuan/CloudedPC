from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from PIL import Image
import re, json, hashlib

BASE = Path(__file__).resolve().parents[1]
WORK = BASE / 'diagram_sources'
ASSETS = BASE / 'assets/report-diagrams'
STEM = 'Dot云电脑软硬件配置与运行检查报告'
manifest = json.loads((WORK / 'diagram-manifest.json').read_text())
assert len(manifest) == 8
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(WORK / 'report-before-diagrams-2026-11-15.md') == '0244937bbd72e40422435599c78eaf13d061c550955066a91f5222fd813af753'
assert sha(WORK / 'report-before-diagrams-2026-11-15.docx') == '600b6123097271bb9599c04d7369fb2da58ceb0c53575a7b1aff17e58b3639dd'

old_md = (WORK / 'report-before-diagrams-2026-11-15.md').read_text()
new_md = (BASE / (STEM + '.md')).read_text()
stripped = re.sub(r'<!-- diagram:[^>]+ -->.*?<!-- /diagram:[^>]+ -->', '', new_md, flags=re.S)
stripped = re.sub(r'<!-- figure-update-notice -->.*?<!-- /figure-update-notice -->', '', stripped, flags=re.S)
normalize = lambda s: '\n'.join(line.rstrip() for line in s.splitlines() if line.strip())
assert normalize(stripped) == normalize(old_md), 'Original Markdown changed'
assert len(re.findall(r'^!\[', new_md, re.M)) == 8
assert re.findall(r'^\[[^\]]+\]: .+$', new_md, re.M) == re.findall(r'^\[[^\]]+\]: .+$', old_md, re.M)
relative_links = []
for md_file in [BASE / (STEM + '.md'), BASE / '图件说明与来源索引.md']:
    for target in re.findall(r'\]\(([^)]+)\)', md_file.read_text()):
        if not target.startswith(('http:', 'https:', '/', '#')):
            assert (BASE / target).is_file(), target
            relative_links.append(target)

with ZipFile(WORK / 'report-before-diagrams-2026-11-15.docx') as z:
    old_parts = {n: z.read(n) for n in z.namelist()}
with ZipFile(BASE / (STEM + '.docx')) as z:
    assert z.testzip() is None
    new_parts = {n: z.read(n) for n in z.namelist()}
changes = {'word/document.xml', 'word/_rels/document.xml.rels', '[Content_Types].xml', 'word/footer1.xml'}
assert all(new_parts[n] == data for n, data in old_parts.items() if n not in changes)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main', 'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
old_doc, new_doc = (E.fromstring(p['word/document.xml']) for p in (old_parts, new_parts))
def signature(el):
    return (el.tag, tuple(sorted(el.attrib.items())), el.text, tuple(signature(c) for c in el))
old_body = list(old_doc.find('w:body', ns))
new_body = list(new_doc.find('w:body', ns))
cursor = 0
for original in old_body:
    while cursor < len(new_body) and signature(new_body[cursor]) != signature(original):
        cursor += 1
    assert cursor < len(new_body), 'Original body element absent or altered'
    cursor += 1
assert len(old_doc.findall('.//w:tbl', ns)) == len(new_doc.findall('.//w:tbl', ns)) == 9
assert len(new_doc.findall('.//wp:inline', ns)) == 8
assert not new_doc.findall('.//wp:anchor', ns)
assert all(el.get('descr') for el in new_doc.findall('.//wp:docPr', ns))
old_rels, new_rels = (E.fromstring(p['word/_rels/document.xml.rels']) for p in (old_parts, new_parts))
rels_by_id = {e.get('Id'): dict(e.attrib) for e in new_rels}
assert all(rels_by_id[e.get('Id')] == dict(e.attrib) for e in old_rels)
for e in new_rels:
    if e.get('TargetMode') == 'External' and not e.get('Target').startswith(('http:', 'https:', '/', 'file:')):
        assert (BASE / e.get('Target')).is_file(), e.get('Target')

full = E.parse(str(ASSETS / 'Dot云电脑完整图集.drawio')).getroot()
assert len(full.findall('diagram')) == 8
counts = []
for i, f in enumerate(manifest, 1):
    key = f['key']
    one = E.parse(str(ASSETS / (key + '.drawio'))).getroot().find('diagram')
    page = full.findall('diagram')[i - 1]
    assert signature(one) == signature(page)
    cells = page.findall('.//mxCell')
    ids = {e.get('id') for e in cells}
    assert len(ids) == len(cells)
    for e in cells:
        assert 'image=' not in e.get('style', '')
        for a in ['parent', 'source', 'target']:
            assert e.get(a) is None or e.get(a) in ids
    assert any(e.get('edge') == '1' for e in cells)
    svg = E.parse(str(ASSETS / (key + '.svg')))
    assert not svg.xpath('//*[local-name()="image"]')
    with Image.open(ASSETS / (key + '.png')) as im:
        assert im.size == (f['width'] * 2, f['height'] * 2)
        im.verify()
    with Image.open(WORK / ('drawio-qa-' + str(i) + '.png')) as im:
        assert im.width > 1000 and im.height > 900
        im.verify()
    assert new_parts['word/media/' + key + '.png'] == (ASSETS / (key + '.png')).read_bytes()
    counts.append({'key': key, 'native_cells': len(cells)})

final_render = BASE / 'fidelity-illustrated-final/b_render'
qa_render = BASE / 'qa-illustrated-2'
assert len(list(final_render.glob('page-*.png'))) == 20
for i in range(1, 21):
    a = final_render / f'page-{i}.png'
    b = qa_render / f'page-{i}.png'
    with Image.open(a) as ia, Image.open(b) as ib:
        assert ia.size == ib.size and ia.tobytes() == ib.tobytes()

files = [BASE / (STEM + '.docx'), BASE / (STEM + '.md'), BASE / '图件说明与来源索引.md'] + sorted(ASSETS.iterdir())
assert len(files) == 28 and all(p.is_file() for p in files)
package = BASE / (STEM + '-图文及可编辑源文件.zip')
with ZipFile(package, 'w', ZIP_DEFLATED) as z:
    for p in files:
        z.write(p, p.relative_to(BASE).as_posix())
with ZipFile(package) as z:
    assert z.testzip() is None
    names = set(z.namelist())
    assert len(names) == 28
    assert all(target in names for target in relative_links)
    assert all(z.read(p.relative_to(BASE).as_posix()) == p.read_bytes() for p in files)

result = {'status': 'PASS', 'word_pages': 20, 'figures': 8, 'original_body_elements_preserved': len(old_body), 'original_tables_preserved': 9, 'source_references_preserved': 21, 'docx_parts_unchanged': len(old_parts) - len(changes), 'native_drawio_pages': counts, 'relative_links_resolve': len(relative_links), 'render_pixel_equivalence': True, 'package_entries': len(files), 'package_bytes': package.stat().st_size, 'sha256_docx': sha(BASE / (STEM + '.docx')), 'sha256_zip': sha(package)}
(WORK / 'final-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False, indent=2))
