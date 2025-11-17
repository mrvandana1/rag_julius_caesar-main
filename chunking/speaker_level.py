# ===============================================================
# Julius Caesar Chunking Script (VS Code version)
# ===============================================================

import re
import json
import pdfplumber
from collections import Counter

# ---------- Local Paths (CHANGE THESE IF NEEDED) ----------
PDF_PATH = "./julius-caesar.pdf"
OUT_PATH = "./julius_caesar_chunks.jsonl"

# ---------- Regex patterns ----------
FTLN_INLINE = re.compile(r"\bFTLN\s*\d+\b")
INLINE_NUM = re.compile(r"\b\d{1,3}\b")
STANDALONE_NUM = re.compile(r"^\s*\d+\s*$")
HEADER_RE  = re.compile(r"^\s*\d*\s*Julius Caesar\b.*", re.IGNORECASE)

ACT_RE   = re.compile(r"^\s*ACT\s+([IVXLC\d]+)\s*$", re.IGNORECASE)
SCENE_RE = re.compile(r"^\s*SCENE\s+([IVXLC\d]+)\s*$", re.IGNORECASE)

STAGE_DIR_CUES = [
    "Enter", "Exit", "Exeunt", "Flourish", "Thunder",
    "Sennet", "Re-enter", "Trumpet", "Alarum"
]

# ---------- Helper functions ----------
def clean_line(line: str) -> str:
    line = FTLN_INLINE.sub("", line)
    line = INLINE_NUM.sub("", line)
    line = re.sub(r"\s{2,}", " ", line).strip()
    return line

def is_stage_direction_start(line: str) -> bool:
    l = line.strip()
    return any(l.startswith(cue) for cue in STAGE_DIR_CUES)

def count_words(text):
    return len(re.findall(r"[a-zA-Z0-9]+", text))

def is_speaker_line_candidate(line: str):
    trimmed = line.strip()
    if not trimmed:
        return None
    m = re.match(r"^([A-Z][A-Z\s,'.-]+?)\.?\s*$", trimmed)
    if not m:
        return None
    speaker = m.group(1).strip()
    non_speakers = [
        'ACT', 'SCENE', 'EPILOGUE', 'PROLOGUE', 'CHORUS', 'CONTENTS',
        'THE END', 'FINIS', 'DRAMATIS PERSONAE', 'PERSONS REPRESENTED',
        'INDUCTION', 'ARGUMENT', 'ENTER', 'EXIT', 'EXEUNT', 'ALARUM',
        'FLOURISH', 'SENNET', 'HAUTBOYS', 'TRUMPETS', 'DRUMS'
    ]
    if (
        1 < len(speaker) < 50
        and not any(speaker.startswith(ns) for ns in non_speakers)
        and not re.match(r"^(ACT|SCENE|ENTER|EXIT|EXEUNT)", speaker)
        and not re.match(r"^\d+$", speaker)
        and not re.match(r"^[IVX]+$", speaker)
    ):
        return speaker
    return None

def strip_trailing_header_artifacts(text: str) -> str:
    text = re.sub(r"\s*Julius\s+Caesar.*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bACT\s*\.\s*SC\.\s*$", "", text).strip()
    return text

# ---------- Main processing ----------
def process_pdf(pdf_path):
    chunks = []
    act = None
    scene = None
    current_speaker = None
    current_text = ""
    chunk_id = 0

    def save_chunk(force_speaker=None):
        nonlocal chunk_id, current_text, current_speaker
        txt = (current_text or "").strip()
        if not txt:
            current_text = ""
            return

        txt = strip_trailing_header_artifacts(txt)
        if not txt:
            current_text = ""
            return

        chunks.append({
            "id": chunk_id,
            "act": act,
            "scene": scene,
            "speaker": force_speaker if force_speaker else current_speaker,
            "type": "speech" if (force_speaker or current_speaker) else "narration",
            "text": txt,
            "textLength": len(txt),
            "wordCount": count_words(txt)
        })
        chunk_id += 1
        current_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[8:]:
            raw_lines = (page.extract_text() or "").splitlines()
            idx = 0
            n = len(raw_lines)

            while idx < n:
                raw = raw_lines[idx].rstrip()
                idx += 1

                if not raw:
                    continue
                if STANDALONE_NUM.match(raw) or HEADER_RE.match(raw):
                    continue

                if re.match(r"^\s*ACT\s+[IVXLC\d]+", raw, re.IGNORECASE):
                    save_chunk()
                    act = re.sub(r"^\s*ACT\s+", "", raw, flags=re.IGNORECASE).strip()
                    scene = None
                    continue

                if re.match(r"^\s*SCENE\s+[IVXLC\d]+", raw, re.IGNORECASE):
                    save_chunk()
                    scene = re.sub(r"^\s*SCENE\s+", "", raw, flags=re.IGNORECASE).strip()
                    continue

                line = clean_line(raw)
                if not line:
                    continue

                if is_stage_direction_start(line):
                    save_chunk()
                    segs = [line]

                    while idx < n:
                        look = raw_lines[idx]
                        look_clean = clean_line(look)

                        if STANDALONE_NUM.match(look) or HEADER_RE.match(look):
                            idx += 1
                            continue

                        if (
                            is_speaker_line_candidate(look_clean)
                            or re.match(r"^\s*ACT\s+[IVXLC\d]+", look, re.IGNORECASE)
                            or re.match(r"^\s*SCENE\s+[IVXLC\d]+", look, re.IGNORECASE)
                        ):
                            break

                        segs.append(look_clean)
                        idx += 1

                    full_stage = strip_trailing_header_artifacts(" ".join(segs).strip())

                    chunks.append({
                        "id": chunk_id,
                        "act": act,
                        "scene": scene,
                        "speaker": None,
                        "type": "stage_direction",
                        "text": full_stage,
                        "textLength": len(full_stage),
                        "wordCount": count_words(full_stage)
                    })
                    chunk_id += 1
                    continue

                multi_segments = re.split(r"(?=\b[A-Z][A-Z\s]{2,}\b)", line)

                for seg in multi_segments:
                    seg = seg.strip()
                    if not seg:
                        continue

                    first_tok = seg.split(" ")[0]
                    speaker_candidate = is_speaker_line_candidate(first_tok)

                    if speaker_candidate:
                        save_chunk()
                        current_speaker = first_tok
                        remaining = " ".join(seg.split(" ")[1:]).strip()
                        current_text = remaining
                    else:
                        current_text += (" " + seg if current_text else seg)

    save_chunk()
    return chunks

# ---------- Run ----------
print("📘 Extracting and chunking Julius Caesar PDF...")
chunks = process_pdf(PDF_PATH)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    for ch in chunks:
        f.write(json.dumps(ch, ensure_ascii=False) + "\n")

type_counts = Counter([c["type"] for c in chunks])
print("\n✅ Chunking complete!")
print(f"Total chunks: {len(chunks)}")
print(f"Chunks by type: {dict(type_counts)}")
