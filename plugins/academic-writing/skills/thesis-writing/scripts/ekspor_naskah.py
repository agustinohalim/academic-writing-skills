"""Export thesis chapters written in Markdown to DOCX and/or PDF in the campus format.

The Markdown chapters are the source; DOCX and PDF are exports. The script:

    1. collects the chapter files — in the order given, or every .md in a folder sorted by name
       with numbers compared as numbers (bab_10.md after bab_9.md); names starting with _ or .
       are skipped;
    2. scans them for leftover placeholders (⬜, [PERLU ...], TODO, XX, ???) and refuses to export
       unless --draft is given;
    3. joins them with a page break before every file except the first;
    4. builds a reference.docx from pandoc's default (or uses --templat) and sets A4 paper,
       margins, font on every style, font size, line spacing, and black headings;
    5. runs pandoc to DOCX (with --citeproc when --bib is given), and makes the PDF from that DOCX
       with LibreOffice, or with pandoc --pdf-engine typst / xelatex when LibreOffice is absent.

Requirements: Python 3.10+ (standard library only) and pandoc. PDF needs LibreOffice (soffice),
Typst, or xelatex. Nothing is uploaded; everything runs locally.

Usage:
    python ekspor_naskah.py bab/ --out Skripsi_Budi --docx --pdf
    python ekspor_naskah.py bab_1.md bab_2.md bab_3.md --out Proposal --docx --draft
    python ekspor_naskah.py bab/ --out Skripsi --docx --margin 4 3 3 3 --spasi 2
    python ekspor_naskah.py bab/ --out Skripsi --docx --bib pustaka.bib --csl apa.csl
    python ekspor_naskah.py bab/ --out Skripsi --docx --templat templat_prodi.docx

Exit codes: 0 exported, 1 placeholders found or a tool is missing, 2 bad arguments.
"""

import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

PENANDA = re.compile(r"⬜|\[PERLU[^\]]*\]|\bTODO\b|\bXX+\b|\?\?\?")
PEMISAH_HALAMAN = (
    "\n\n```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```\n\n"
    "```{=latex}\n\\newpage\n```\n\n"
    "```{=typst}\n#pagebreak()\n```\n\n"
)
A4_TWIPS = (11906, 16838)  # width, height
TWIPS_PER_CM = 566.929


# ---------------------------------------------------------------- chapters

def kunci_alami(nama):
    """Sort key that compares digit runs as numbers: bab_2 < bab_10."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", nama)]


def kumpulkan_bab(masukan):
    """Return the chapter files in export order from files and/or folders."""
    hasil = []
    for jalur in masukan:
        if os.path.isdir(jalur):
            nama = [n for n in os.listdir(jalur)
                    if n.lower().endswith(".md") and not n.startswith(("_", "."))]
            hasil.extend(os.path.join(jalur, n) for n in sorted(nama, key=kunci_alami))
        elif os.path.isfile(jalur):
            hasil.append(jalur)
        else:
            raise FileNotFoundError(jalur)
    return hasil


def cari_penanda(berkas):
    """List (file, line number, marker, line text) for every leftover placeholder."""
    temuan = []
    for jalur in berkas:
        with open(jalur, encoding="utf-8") as f:
            for no, baris in enumerate(f, 1):
                for m in PENANDA.finditer(baris):
                    temuan.append((jalur, no, m.group(0), baris.strip()))
    return temuan


def gabung_bab(berkas):
    bagian = []
    for jalur in berkas:
        with open(jalur, encoding="utf-8") as f:
            bagian.append(f.read().strip("\n"))
    return PEMISAH_HALAMAN.join(bagian) + "\n"


# ---------------------------------------------------------------- reference.docx

def cm_ke_twips(cm):
    return int(round(cm * TWIPS_PER_CM))


def _atur_halaman(xml, margin_cm):
    kiri, atas, kanan, bawah = (cm_ke_twips(x) for x in margin_cm)
    pgsz = f'<w:pgSz w:w="{A4_TWIPS[0]}" w:h="{A4_TWIPS[1]}"/>'
    pgmar = (f'<w:pgMar w:top="{atas}" w:right="{kanan}" w:bottom="{bawah}" w:left="{kiri}" '
             f'w:header="708" w:footer="708" w:gutter="0"/>')
    xml = re.sub(r"<w:pgSz\b[^>]*/>", "", xml)
    xml = re.sub(r"<w:pgMar\b[^>]*/>", "", xml)
    if re.search(r"<w:sectPr\b[^>]*/>", xml):
        xml = re.sub(r"<w:sectPr\b([^>]*)/>", rf"<w:sectPr\1>{pgsz}{pgmar}</w:sectPr>", xml)
    elif "<w:sectPr" in xml:
        xml = re.sub(r"(<w:sectPr\b[^>]*>)", rf"\1{pgsz}{pgmar}", xml)
    else:
        xml = xml.replace("</w:body>", f"<w:sectPr>{pgsz}{pgmar}</w:sectPr></w:body>")
    return xml


def _atur_gaya(xml, font, ukuran_pt, spasi):
    rfonts = f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" w:cs="{font}"/>'
    half = int(round(ukuran_pt * 2))
    line = int(round(spasi * 240))
    # every style uses the thesis font; heading colours removed (black headings)
    xml = re.sub(r"<w:rFonts\b[^>]*/>", rfonts, xml)
    xml = re.sub(r"<w:color\b[^>]*/>", "", xml)
    # document defaults: font, size, line spacing
    rpr_def = f"<w:rPrDefault><w:rPr>{rfonts}<w:sz w:val=\"{half}\"/><w:szCs w:val=\"{half}\"/></w:rPr></w:rPrDefault>"
    ppr_def = f'<w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="{line}" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
    xml = re.sub(r"<w:rPrDefault\b.*?</w:rPrDefault>|<w:rPrDefault\s*/>", "", xml, flags=re.S)
    xml = re.sub(r"<w:pPrDefault\b.*?</w:pPrDefault>|<w:pPrDefault\s*/>", "", xml, flags=re.S)
    if "<w:docDefaults" in xml:
        xml = re.sub(r"<w:docDefaults\s*/>", "<w:docDefaults></w:docDefaults>", xml)
        xml = re.sub(r"(<w:docDefaults\b[^>]*>)", rf"\1{rpr_def}{ppr_def}", xml, count=1)
    else:
        xml = re.sub(r"(<w:styles\b[^>]*>)", rf"\1<w:docDefaults>{rpr_def}{ppr_def}</w:docDefaults>",
                     xml, count=1)
    # body styles carry their own line spacing in pandoc's reference.docx; make them follow
    xml = re.sub(r'(<w:spacing\b[^>]*?)\sw:line="\d+"', r"\1", xml)
    xml = re.sub(r'(<w:spacing\b[^>]*?)\sw:lineRule="\w+"', r"\1", xml)
    xml = re.sub(r"<w:spacing\b(?![^>]*w:line=)([^>]*)/>",
                 rf'<w:spacing\1 w:line="{line}" w:lineRule="auto"/>', xml)
    # explicit sizes in styles other than headings and title follow the body size
    def ganti_ukuran(m):
        blok = m.group(0)
        if re.search(r'w:styleId="(Heading\d|Title|Subtitle)"', blok):
            return blok
        blok = re.sub(r'<w:sz w:val="\d+"/>', f'<w:sz w:val="{half}"/>', blok)
        return re.sub(r'<w:szCs w:val="\d+"/>', f'<w:szCs w:val="{half}"/>', blok)
    return re.sub(r"<w:style\b.*?</w:style>", ganti_ukuran, xml, flags=re.S)


def ubah_reference_docx(data, margin_cm=(4, 4, 3, 3), font="Times New Roman",
                        ukuran_pt=12, spasi=1.5):
    """Return a modified copy of a reference.docx (bytes in, bytes out).

    Sets A4 paper and margins (left, top, right, bottom in cm) in word/document.xml, and the
    font, size, line spacing, and black headings in word/styles.xml. Other parts are copied.
    """
    masuk = zipfile.ZipFile(io.BytesIO(data))
    keluar_buf = io.BytesIO()
    with zipfile.ZipFile(keluar_buf, "w", zipfile.ZIP_DEFLATED) as keluar:
        for info in masuk.infolist():
            isi = masuk.read(info.filename)
            if info.filename == "word/document.xml":
                isi = _atur_halaman(isi.decode("utf-8"), margin_cm).encode("utf-8")
            elif info.filename == "word/styles.xml":
                isi = _atur_gaya(isi.decode("utf-8"), font, ukuran_pt, spasi).encode("utf-8")
            keluar.writestr(info, isi)
    return keluar_buf.getvalue()


# ---------------------------------------------------------------- external tools

def jalankan(perintah):
    hasil = subprocess.run(perintah, capture_output=True, text=True)
    if hasil.returncode != 0:
        raise RuntimeError(f"{perintah[0]} gagal ({hasil.returncode}): {hasil.stderr.strip()}")
    return hasil


def reference_bawaan_pandoc(pandoc, tujuan):
    jalankan([pandoc, "-o", tujuan, "--print-default-data-file", "reference.docx"])


def ke_docx(pandoc, md, docx, reference, bib=None, csl=None):
    perintah = [pandoc, md, "-f", "markdown", "-o", docx, "--reference-doc", reference]
    perintah += opsi_sitasi(bib, csl)
    jalankan(perintah)


def opsi_sitasi(bib, csl):
    opsi = []
    if bib:
        opsi += ["--citeproc", "--bibliography", bib]
        if csl:
            opsi += ["--csl", csl]
    return opsi


def pdf_dari_docx(soffice, docx, pdf):
    folder = tempfile.mkdtemp()
    try:
        jalankan([soffice, "--headless", "--convert-to", "pdf", "--outdir", folder, docx])
        nama = os.path.splitext(os.path.basename(docx))[0] + ".pdf"
        shutil.move(os.path.join(folder, nama), pdf)
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def metadata_pdf(margin_cm, font, ukuran_pt, spasi):
    kiri, atas, kanan, bawah = margin_cm
    return (
        "papersize: a4\n"
        f"geometry: \"left={kiri}cm, top={atas}cm, right={kanan}cm, bottom={bawah}cm\"\n"
        f"margin:\n  left: {kiri}cm\n  top: {atas}cm\n  right: {kanan}cm\n  bottom: {bawah}cm\n"
        f"mainfont: \"{font}\"\n"
        f"fontsize: {ukuran_pt}pt\n"
        f"linestretch: {spasi}\n"
    )


def pdf_dengan_pandoc(pandoc, mesin, md, pdf, meta, bib=None, csl=None):
    perintah = [pandoc, md, "-f", "markdown", "-o", pdf, "--pdf-engine", mesin,
                "--metadata-file", meta]
    jalankan(perintah + opsi_sitasi(bib, csl))


def cari_alat(*nama):
    for n in nama:
        jalur = shutil.which(n)
        if jalur:
            return jalur
    return None


# ---------------------------------------------------------------- main

def baca_argumen(argv):
    p = argparse.ArgumentParser(description="Export thesis chapters (Markdown) to DOCX/PDF.")
    p.add_argument("masukan", nargs="+", help="chapter .md files in order, or a folder")
    p.add_argument("--out", required=True, help="output path without extension")
    p.add_argument("--docx", action="store_true", help="write <out>.docx (default when no format given)")
    p.add_argument("--pdf", action="store_true", help="write <out>.pdf")
    p.add_argument("--margin", nargs=4, type=float, default=[4, 4, 3, 3],
                   metavar=("KIRI", "ATAS", "KANAN", "BAWAH"), help="margins in cm (default 4 4 3 3)")
    p.add_argument("--font", default="Times New Roman")
    p.add_argument("--ukuran", type=float, default=12, help="font size in pt (default 12)")
    p.add_argument("--spasi", type=float, default=1.5, help="line spacing (default 1.5)")
    p.add_argument("--bib", help="BibTeX/CSL-JSON bibliography for pandoc --citeproc")
    p.add_argument("--csl", help="CSL citation style file (with --bib)")
    p.add_argument("--templat", help="campus reference .docx used instead of the generated one")
    p.add_argument("--draft", action="store_true", help="export even when placeholders remain")
    a = p.parse_args(argv)
    if not a.docx and not a.pdf:
        a.docx = True
    if a.csl and not a.bib:
        p.error("--csl needs --bib")
    return a


def main(argv=None):
    for aliran in (sys.stdout, sys.stderr):
        try:
            aliran.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    a = baca_argumen(sys.argv[1:] if argv is None else argv)
    try:
        berkas = kumpulkan_bab(a.masukan)
    except FileNotFoundError as e:
        print(f"Not found: {e}", file=sys.stderr)
        return 2
    if not berkas:
        print("No .md chapter files found.", file=sys.stderr)
        return 2

    penanda = cari_penanda(berkas)
    if penanda:
        for jalur, no, tanda, baris in penanda:
            print(f"  {jalur}:{no}: {tanda}  | {baris[:100]}")
        if not a.draft:
            print(f"Refused: {len(penanda)} placeholder(s) left. Fill them, or add --draft "
                  "for a supervision draft.", file=sys.stderr)
            return 1
        print(f"Draft export: {len(penanda)} placeholder(s) left in the text.")

    pandoc = cari_alat("pandoc")
    if not pandoc:
        print("pandoc not found. Install it from https://pandoc.org/installing.html", file=sys.stderr)
        return 1
    soffice = cari_alat("soffice", "libreoffice")
    mesin = None if soffice else cari_alat("typst", "xelatex")
    if a.pdf and not soffice and not mesin:
        print("No PDF engine: install LibreOffice (preferred), Typst, or a LaTeX engine (xelatex).",
              file=sys.stderr)
        return 1

    folder_out = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(folder_out, exist_ok=True)
    kerja = tempfile.mkdtemp()
    try:
        md = os.path.join(kerja, "naskah.md")
        with open(md, "w", encoding="utf-8") as f:
            f.write(gabung_bab(berkas))

        reference = os.path.join(kerja, "reference.docx")
        if a.templat:
            shutil.copy(a.templat, reference)
        else:
            mentah = os.path.join(kerja, "default.docx")
            reference_bawaan_pandoc(pandoc, mentah)
            with open(mentah, "rb") as f:
                data = ubah_reference_docx(f.read(), a.margin, a.font, a.ukuran, a.spasi)
            with open(reference, "wb") as f:
                f.write(data)

        dibuat = []
        docx = a.out + ".docx" if a.docx else os.path.join(kerja, os.path.basename(a.out) + ".docx")
        if a.docx or soffice:
            ke_docx(pandoc, md, docx, reference, a.bib, a.csl)
            if a.docx:
                dibuat.append(docx)
        if a.pdf:
            pdf = a.out + ".pdf"
            if soffice:
                pdf_dari_docx(soffice, docx, pdf)
            else:
                meta = os.path.join(kerja, "meta.yaml")
                with open(meta, "w", encoding="utf-8") as f:
                    f.write(metadata_pdf(a.margin, a.font, a.ukuran, a.spasi))
                pdf_dengan_pandoc(pandoc, os.path.basename(mesin).split(".")[0], md, pdf, meta,
                                  a.bib, a.csl)
            dibuat.append(pdf)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(kerja, ignore_errors=True)

    print(f"{len(berkas)} chapter file(s) → " + ", ".join(dibuat))
    return 0


if __name__ == "__main__":
    sys.exit(main())
