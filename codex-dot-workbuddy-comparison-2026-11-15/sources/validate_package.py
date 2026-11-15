from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from PIL import Image
import hashlib, json, re

BASE = Path(__file__).resolve().parents[1]
STEM = 'Codex Dot对比 Workbuddy云PC对比分析报告及GUI体验分析'
OUT = BASE / (STEM + '.docx')
MD = BASE / (STEM + '.md')
GUIDE = BASE / '图件与文件使用说明.md'
sources = json.loads((BASE / 'sources/source-index.json').read_text())
manifest = json.loads((BASE / 'sources/diagram-manifest.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for key, item in sources.items():
    if key != 'public_references':
        assert sha(Path(item['path'])) == item['sha256'], key
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
qn = lambda s: '{'+ns['w']+'}'+s
mutable = {'word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml',
           'word/footer1.xml','docProps/core.xml','word/settings.xml'}
with ZipFile(OUT) as doc, ZipFile(sources['W2']['path']) as ref:
    assert doc.testzip() is None
    preserved = [n for n in ref.namelist() if n not in mutable]
    assert all(doc.read(n) == ref.read(n) for n in preserved)
    root = E.fromstring(doc.read('word/document.xml'))
    ref_root = E.fromstring(ref.read('word/document.xml'))
    assert E.tostring(root.find('w:body/w:sectPr',ns)) == E.tostring(ref_root.find('w:body/w:sectPr',ns))
    alltext = ''.join(root.itertext())
    assert '{{figure:' not in alltext and 'turn0search' not in alltext
    title = root.xpath('//w:p[w:pPr/w:pStyle[@w:val="Title"]]',namespaces=ns)
    assert len(title) == 1 and ''.join(title[0].xpath('.//w:t/text()',namespaces=ns)) == STEM
    headings = root.xpath('//w:p[w:pPr/w:pStyle[@w:val="Heading1"]]',namespaces=ns)
    assert len(headings) == 12
    assert len(root.findall('.//wp:inline',ns)) == 6 and not root.findall('.//wp:anchor',ns)
    assert all(p.find(qn('pPr')) is None or list(p)[0].tag == qn('pPr') for p in root.findall('.//w:p',ns))
    rel = E.fromstring(doc.read('word/_rels/document.xml.rels'))
    relmap = {r.get('Id'):dict(r.attrib) for r in rel}
    assert len(relmap) == len(rel)
    for r in E.fromstring(ref.read('word/_rels/document.xml.rels')):
        assert relmap[r.get('Id')] == dict(r.attrib)
    targets = {r.get('Target') for r in rel}
    refs = dict(re.findall(r'^\[([^\]]+)\]: (.+)$',MD.read_text(),re.M))
    assert len(refs) == 17 and set(refs.values()).issubset(targets)
    assert E.fromstring(doc.read('word/settings.xml')).find(qn('updateFields')).get(qn('val')) == 'true'
    assert 'PAGE' in doc.read('word/footer1.xml').decode()
    for f in manifest:
        assert doc.read('word/media/'+f['key']+'.png') == (BASE/'assets/report-diagrams'/ (f['key']+'.png')).read_bytes()
    tables = len(root.findall('.//w:tbl',ns))

# Each Markdown source paragraph/cell is preserved in the Word body.
author = (BASE / '报告正文.md').read_text()
for line in author.splitlines():
    line = line.strip()
    if not line or line.startswith('{{figure:') or re.match(r'^\[[^\]]+\]: ',line):
        continue
    if line.startswith('|'):
        cells = [c.strip() for c in line.strip('|').split('|')]
        if all(re.fullmatch(r'[-: ]+',c) for c in cells):
            continue
        fragments = cells
    else:
        fragments = [re.sub(r'^#+ ', '', line)]
    for fragment in fragments:
        assert fragment.replace('**','') in alltext, fragment

assets = sorted((BASE/'assets/report-diagrams').iterdir())
assert len(assets) == 19
full = E.parse(str(BASE/'assets/report-diagrams/CodexDot与WorkBuddy完整图集.drawio'))
pages = full.findall('diagram')
assert len(pages) == 6
graphs = []
for i,f in enumerate(manifest):
    prefix = BASE/'assets/report-diagrams'/f['key']
    with Image.open(prefix.with_suffix('.png')) as img:
        assert img.size == (f['width']*2,f['height']*2)
    svg = E.parse(str(prefix.with_suffix('.svg')))
    assert not svg.xpath('//*[local-name()="image"]')
    single = E.parse(str(prefix.with_suffix('.drawio'))).find('diagram')
    graph = single.find('mxGraphModel')
    assert E.tostring(graph) == E.tostring(pages[i].find('mxGraphModel'))
    cells = graph.findall('.//mxCell')
    ids = {c.get('id') for c in cells}
    assert len(ids) == len(cells)
    for c in cells:
        for key in ['parent','source','target']:
            assert c.get(key) is None or c.get(key) in ids
    graphs.append({'key':f['key'],'vertices':sum(c.get('vertex')=='1' for c in cells),
                   'edges':sum(c.get('edge')=='1' for c in cells)})

relative_links = []
for p in [MD,GUIDE]:
    text = p.read_text()
    assert '{{figure:' not in text
    for href in re.findall(r'\]\(([^)]+)\)',text):
        if href.startswith(('https://','http://','#')):
            continue
        target = Path(href) if href.startswith('/') else BASE/href
        assert target.is_file(), href
        if not href.startswith('/'):
            relative_links.append(href)
render = BASE/'qa-2/b_render'
assert {p.name for p in render.glob('page-*.png')} == {f'page-{i}.png' for i in range(1,20)}
files = [OUT, MD, GUIDE] + assets
zip_path = BASE/(STEM+'-完整交付包.zip')
with ZipFile(zip_path,'w',ZIP_DEFLATED) as z:
    for p in files:
        z.write(p,p.relative_to(BASE))
with ZipFile(zip_path) as z:
    assert len(z.namelist()) == 22 and z.testzip() is None
    assert set(relative_links).issubset(set(z.namelist()))
    for p in files:
        assert z.read(str(p.relative_to(BASE))) == p.read_bytes()
report = {'status':'pass','word_pages':19,'visually_reviewed_pages':list(range(1,20)),
          'native_drawio_exports_visually_reviewed':6,'figures':6,'tables':tables,
          'chapters':12,'source_ids':list(refs),'preserved_template_parts':len(preserved),
          'source_hashes_unchanged':True,'relative_links_valid':True,'native_graphs':graphs,
          'zip_entries':22,'zip_crc':'pass','output_sha256':sha(OUT),'zip_sha256':sha(zip_path),
          'accessibility_audit':'0 findings (prior audit)','final_render':'qa-2/b_render'}
(BASE/'sources/final-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (BASE/'sources/artifact.md').open('a') as f:
    f.write('\nFinal verification: final qa-2 render has 19 pages, all visually inspected; six native draw.io exports visually inspected. All source hashes unchanged, preserve-only template parts and original relationships retained, PAGE field retained, 17 source links valid. Six PNG/SVG/native draw.io sets plus combined six-page draw.io pass structure checks. ZIP has 22 byte-verified entries and passes CRC. See final-validation.json.\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
print(zip_path)
