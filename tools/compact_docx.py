"""Apply the report's compact type and pagination settings to the generated DOCX."""

import argparse
from pathlib import Path
from xml.dom import minidom
from zipfile import ZipFile


def child(parent, name, *, first=False):
    tag = f"w:{name}"
    for node in parent.childNodes:
        if getattr(node, "tagName", None) == tag:
            return node
    node = parent.ownerDocument.createElement(tag)
    if first and parent.firstChild:
        parent.insertBefore(node, parent.firstChild)
    else:
        parent.appendChild(node)
    return node


def apply(element, **attributes):
    for name, value in attributes.items():
        element.setAttribute(f"w:{name}", str(value))


def size(run, half_points):
    for name in ("sz", "szCs"):
        apply(child(run, name), val=half_points)


def style_xml(content):
    xml = minidom.parseString(content)
    defaults = xml.getElementsByTagName("w:docDefaults")[0]
    size(child(child(defaults, "rPrDefault"), "rPr"), 21)
    normal = child(child(defaults, "pPrDefault"), "pPr")
    apply(child(normal, "spacing"), after=36, line=240, lineRule="auto")
    styles = {style.getAttribute("w:styleId"): style for style in xml.getElementsByTagName("w:style")}
    for level, before, after in [(1, 160, 70), (2, 125, 55), (3, 100, 45), (4, 80, 30)]:
        paragraph = child(styles[f"Heading{level}"], "pPr")
        child(paragraph, "keepNext", first=True)
        apply(child(paragraph, "spacing"), before=before, after=after)
    code = styles["SourceCode"]
    ppr = child(code, "pPr")
    apply(child(ppr, "spacing"), before=20, after=45, line=240, lineRule="auto")
    size(child(code, "rPr"), 19)
    return xml.toxml(encoding="UTF-8")


def document_xml(content):
    xml = minidom.parseString(content)
    for section in xml.getElementsByTagName("w:sectPr"):
        apply(child(section, "pgMar"), top=820, right=850, bottom=820, left=850)
    for paragraph in xml.getElementsByTagName("w:p"):
        entries = paragraph.getElementsByTagName("w:t")
        title = "".join(entry.firstChild.data for entry in entries if entry.firstChild)
        if title == "References":
            child(child(paragraph, "pPr", first=True), "pageBreakBefore", first=True)
    for cell in xml.getElementsByTagName("w:tc"):
        for paragraph in cell.getElementsByTagName("w:p"):
            ppr = child(paragraph, "pPr", first=True)
            apply(child(ppr, "spacing"), before=0, after=0, line=240, lineRule="auto")
            size(child(ppr, "rPr"), 19)
            for run in paragraph.getElementsByTagName("w:r"):
                size(child(run, "rPr", first=True), 19)
    for row in xml.getElementsByTagName("w:tr"):
        child(child(row, "trPr", first=True), "cantSplit", first=True)
    return xml.toxml(encoding="UTF-8")


def main(path):
    transforms = {"word/styles.xml": style_xml, "word/document.xml": document_xml}
    temporary = path.with_suffix(".tmp")
    with ZipFile(path) as source, ZipFile(temporary, "w") as output:
        for entry in source.infolist():
            payload = source.read(entry)
            if entry.filename in transforms:
                payload = transforms[entry.filename](payload)
            output.writestr(entry, payload)
    temporary.replace(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    main(parser.parse_args().document)
