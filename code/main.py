"""
ProofLayer Backend - AI Compliance Engine
Built for: c0mpiled-10/DC AI for Government Hackathon

Run with:
    pip install -r requirements.txt
    python main.py
"""

import io
import os
import json
import uuid
import pathlib
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# ── Local modules ──────────────────────────────────────────────────────────────
from llm import call_llm, get_cost_summary, route_task
from controls import CONTROL_DATASET, FRAMEWORKS

# ── Optional deps (graceful fallback if not installed) ────────────────────────
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ProofLayer API",
    description="AI-powered compliance auditing for government contractors",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = pathlib.Path("uploads")
REPORT_DIR = pathlib.Path("reports")
UPLOAD_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

# In-memory audit store (use a DB in production)
audit_store: dict[str, dict] = {}


# ── Request / Response models ─────────────────────────────────────────────────
class AuditRequest(BaseModel):
    doc_id: str
    frameworks: list[str] = ["FedRAMP", "CMMC", "NIST_800_53"]
    model_override: Optional[str] = None
    prefer_local: bool = False


class FixRequest(BaseModel):
    control_id: str
    control_name: str
    framework: str = "FedRAMP"
    model_override: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────
def extract_text_from_bytes(content: bytes, filename: str) -> str:
    """Extract text from PDF or plain text files."""
    if filename.lower().endswith(".pdf") and PDF_AVAILABLE:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    # Fallback: treat as plain text
    try:
        return content.decode("utf-8", errors="replace")
    except Exception:
        return ""


def keyword_map(text: str) -> list[dict]:
    """Fast keyword-based control mapping (no LLM needed)."""
    text_lower = text.lower()
    matched = []
    seen_ids = set()
    for ctrl in CONTROL_DATASET:
        if ctrl["id"] in seen_ids:
            continue
        if any(kw in text_lower for kw in ctrl["keywords"]):
            matched.append(ctrl)
            seen_ids.add(ctrl["id"])
    return matched


def compute_score(matched: list[dict], total: int) -> int:
    return min(100, int(len(matched) / max(total, 1) * 100))


def risk_level(score: int) -> str:
    if score >= 80:
        return "LOW"
    if score >= 55:
        return "MEDIUM"
    return "HIGH"


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ProofLayer API running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok", "pdf_support": PDF_AVAILABLE, "report_export": REPORTLAB_AVAILABLE}


@app.get("/frameworks")
def list_frameworks():
    return {"frameworks": FRAMEWORKS, "total_controls": len(CONTROL_DATASET)}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Accept PDF or text documents. Returns doc_id for subsequent audit.
    Extraction uses gpt-4o-mini (cheap) for AI normalization.
    """
    content = await file.read()
    doc_id = str(uuid.uuid4())[:8]

    # Extract raw text
    raw_text = extract_text_from_bytes(content, file.filename or "doc.txt")
    if not raw_text.strip():
        raise HTTPException(400, "Could not extract text from document.")

    # Save raw text
    (UPLOAD_DIR / f"{doc_id}.txt").write_text(raw_text, encoding="utf-8")

    # AI extraction pass: normalize + identify key security topics
    try:
        ai_result = await call_llm(
            prompt=f"""Extract all security and compliance topics mentioned in this document.
Return a concise list of security practices, policies, controls, and procedures mentioned.
Document:
{raw_text[:6000]}
""",
            task_type="extraction",
            system="You are a security compliance expert. Extract only factual security controls and practices mentioned in the document. Be concise.",
            content_length=len(raw_text),
        )
        extracted_summary = ai_result["text"]
    except Exception as e:
        extracted_summary = raw_text[:3000]  # Fallback to raw text

    # Store for audit
    audit_store[doc_id] = {
        "doc_id":    doc_id,
        "filename":  file.filename,
        "raw_text":  raw_text,
        "summary":   extracted_summary,
        "uploaded":  datetime.utcnow().isoformat(),
    }

    return {
        "doc_id":    doc_id,
        "filename":  file.filename,
        "char_count": len(raw_text),
        "summary":   extracted_summary[:500] + "..." if len(extracted_summary) > 500 else extracted_summary,
    }


@app.post("/audit")
async def run_audit(req: AuditRequest):
    """
    Full compliance audit pipeline:
      1. Keyword mapping (fast, free)
      2. AI gap analysis (gpt-4o — strong reasoning)
      3. Risk scoring
    """
    if req.doc_id not in audit_store:
        raise HTTPException(404, f"Document {req.doc_id} not found. Upload first.")

    doc = audit_store[req.doc_id]
    text = doc["summary"] or doc["raw_text"]

    # Step 1: Keyword mapping (instant, no LLM cost)
    keyword_matched = keyword_map(text)
    keyword_matched_ids = {c["id"] for c in keyword_matched}

    all_controls = CONTROL_DATASET
    total_controls = len(all_controls)

    # Step 2: AI gap analysis — use strong model for reasoning
    gap_prompt = f"""You are a senior FedRAMP and CMMC compliance auditor.

Analyze this document excerpt and determine which of the following security controls have evidence of implementation vs. which are missing/unclear.

Document summary:
{text[:4000]}

Security controls to check:
{json.dumps([{"id": c["id"], "control": c["control"], "keywords": c["keywords"][:3]} for c in all_controls], indent=2)}

Return ONLY valid JSON in this exact format:
{{
  "verified": ["AC-01", "SC-01"],
  "partial": ["CM-01"],
  "missing": ["AU-02", "IR-01"],
  "notes": {{
    "AC-01": "Clear access control policy found",
    "AU-02": "No evidence of automated alerting"
  }}
}}
"""
    try:
        ai_result = await call_llm(
            prompt=gap_prompt,
            task_type="gap_analysis",
            system="You are a strict compliance auditor. Respond only with valid JSON. Never include markdown code fences.",
            model_override=req.model_override,
            content_length=len(text),
            prefer_local=req.prefer_local,
            max_tokens=2000,
        )
        raw_json = ai_result["text"].strip()
        # Strip code fences if present
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]
        ai_analysis = json.loads(raw_json)
    except Exception as e:
        # Fallback: use keyword match results
        ai_analysis = {
            "verified": [c["id"] for c in keyword_matched],
            "partial":  [],
            "missing":  [c["id"] for c in all_controls if c["id"] not in keyword_matched_ids],
            "notes":    {},
        }

    verified_ids = set(ai_analysis.get("verified", []))
    partial_ids  = set(ai_analysis.get("partial", []))
    missing_ids  = set(ai_analysis.get("missing", []))
    ai_notes     = ai_analysis.get("notes", {})

    # Step 3: Build results per framework
    framework_scores: dict[str, dict] = {}
    for fw in req.frameworks:
        fw_controls = [c for c in all_controls if fw in c["frameworks"]]
        fw_verified = [c for c in fw_controls if c["id"] in verified_ids]
        fw_partial  = [c for c in fw_controls if c["id"] in partial_ids]
        fw_score    = compute_score(fw_verified + fw_partial, len(fw_controls))
        framework_scores[fw] = {
            "name":          FRAMEWORKS.get(fw, fw),
            "total_controls": len(fw_controls),
            "verified":      len(fw_verified),
            "partial":       len(fw_partial),
            "score":         fw_score,
        }

    overall_score = compute_score(
        [c for c in all_controls if c["id"] in verified_ids | partial_ids],
        total_controls,
    )

    # Build gap list with remediation
    gaps = []
    for ctrl in all_controls:
        if ctrl["id"] in missing_ids:
            relevant_frameworks = {k: v for k, v in ctrl["frameworks"].items() if k in req.frameworks}
            if not relevant_frameworks:
                continue
            gaps.append({
                "id":          ctrl["id"],
                "control":     ctrl["control"],
                "category":    ctrl["category"],
                "risk":        ctrl["risk"],
                "frameworks":  relevant_frameworks,
                "remediation": ctrl["remediation"],
                "ai_note":     ai_notes.get(ctrl["id"], ""),
            })

    # Build verified list
    verified = []
    for ctrl in all_controls:
        if ctrl["id"] in verified_ids | partial_ids:
            verified.append({
                "id":       ctrl["id"],
                "control":  ctrl["control"],
                "category": ctrl["category"],
                "status":   "VERIFIED" if ctrl["id"] in verified_ids else "PARTIAL",
                "ai_note":  ai_notes.get(ctrl["id"], ""),
            })

    # Store audit result
    audit_id = str(uuid.uuid4())[:8]
    audit_result = {
        "audit_id":          audit_id,
        "doc_id":            req.doc_id,
        "filename":          doc["filename"],
        "overall_score":     overall_score,
        "risk_level":        risk_level(overall_score),
        "framework_scores":  framework_scores,
        "verified_controls": verified,
        "gaps":              gaps,
        "high_risk_gaps":    [g for g in gaps if g["risk"] == "HIGH"],
        "created":           datetime.utcnow().isoformat(),
        "llm_model":         route_task("gap_analysis"),
    }
    audit_store[f"audit_{audit_id}"] = audit_result

    return audit_result


@app.post("/fix")
async def generate_fix(req: FixRequest):
    """
    Generate a missing policy document using gpt-4o.
    This is the 'WOW' feature: not just finding gaps — fixing them instantly.
    """
    prompt = f"""Write a professional, complete {req.control_name} policy document for a federal government contractor.

Requirements:
- Compliant with {req.framework} (control: {req.frameworks if hasattr(req, 'frameworks') else req.framework})
- Include: Purpose, Scope, Policy Statement, Procedures, Roles & Responsibilities, Compliance
- Use clear, formal language appropriate for a federal contractor
- Be specific and actionable
- Length: 400-600 words

Format as a professional policy document with headers.
"""
    try:
        result = await call_llm(
            prompt=prompt,
            task_type="fix_generation",
            system="You are a compliance policy writer for federal government contractors. Write clear, actionable policy documents.",
            model_override=req.model_override,
            max_tokens=1500,
        )
        return {
            "control_id":  req.control_id,
            "control_name": req.control_name,
            "framework":   req.framework,
            "policy_text": result["text"],
            "model":       result["model"],
            "cost_usd":    result["cost_usd"],
        }
    except Exception as e:
        raise HTTPException(500, f"LLM error: {str(e)}")


@app.post("/report/{audit_id}")
async def generate_report(audit_id: str, model_override: Optional[str] = None):
    """
    Generate a professional narrative audit report using gpt-4o.
    """
    key = f"audit_{audit_id}"
    if key not in audit_store:
        raise HTTPException(404, f"Audit {audit_id} not found.")

    result = audit_store[key]

    prompt = f"""Write a professional compliance audit report for a federal government contractor.

Organization Audit Summary:
- Overall Compliance Score: {result['overall_score']}%
- Risk Level: {result['risk_level']}
- Frameworks: {', '.join(result['framework_scores'].keys())}
- Verified Controls: {len(result['verified_controls'])}
- Identified Gaps: {len(result['gaps'])}
- High-Risk Gaps: {len(result['high_risk_gaps'])}

Framework Breakdown:
{json.dumps(result['framework_scores'], indent=2)}

Top Gaps:
{json.dumps([{"control": g["control"], "risk": g["risk"], "remediation": g["remediation"]} for g in result['gaps'][:8]], indent=2)}

Write a formal executive summary (~400 words) covering:
1. Overall compliance posture
2. Key findings by framework
3. Critical gaps requiring immediate action
4. Recommended remediation roadmap
5. Next steps

Use professional language suitable for submission to a federal agency or ISSO.
"""
    try:
        ai_result = await call_llm(
            prompt=prompt,
            task_type="report_generation",
            system="You are a senior GRC consultant writing a formal compliance audit report for a federal contractor.",
            model_override=model_override,
            max_tokens=2000,
        )
        report_text = ai_result["text"]
    except Exception as e:
        report_text = f"Report generation unavailable: {str(e)}"

    result["narrative_report"] = report_text
    return {"audit_id": audit_id, "report": report_text, "model": ai_result.get("model", "unknown")}


@app.get("/export/{audit_id}")
async def export_report_pdf(audit_id: str):
    """
    Export audit results as a professional PDF.
    Returns: downloadable PDF file.
    """
    key = f"audit_{audit_id}"
    if key not in audit_store:
        raise HTTPException(404, f"Audit {audit_id} not found.")

    result = audit_store[key]

    if not REPORTLAB_AVAILABLE:
        # Return JSON fallback
        return JSONResponse(result)

    pdf_path = REPORT_DIR / f"audit_{audit_id}.pdf"
    _generate_pdf(result, str(pdf_path))

    return FileResponse(
        path=str(pdf_path),
        filename=f"ProofLayer_Audit_{audit_id}.pdf",
        media_type="application/pdf",
    )


def _generate_pdf(result: dict, path: str):
    """Generate a professional PDF audit report."""
    doc = SimpleDocTemplate(path, pagesize=letter,
                            leftMargin=inch, rightMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        fontSize=22, spaceAfter=6, textColor=colors.HexColor("#0D2B4E"),
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=13, spaceAfter=4, textColor=colors.HexColor("#1E5799"),
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, spaceAfter=4, leading=14,
    )
    score_style = ParagraphStyle(
        "Score", parent=styles["Normal"],
        fontSize=32, bold=True, textColor=colors.HexColor("#0D7377"),
    )

    story = []

    # Header
    story.append(Paragraph("ProofLayer Compliance Audit Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%B %d, %Y')}", body_style))
    story.append(Paragraph(f"Document: {result.get('filename', 'N/A')}", body_style))
    story.append(HRFlowable(color=colors.HexColor("#1E5799"), thickness=2))
    story.append(Spacer(1, 0.2 * inch))

    # Score
    story.append(Paragraph(f"Overall Compliance Score: {result['overall_score']}%", h2_style))
    story.append(Paragraph(f"Risk Level: {result['risk_level']}", body_style))
    story.append(Spacer(1, 0.2 * inch))

    # Framework breakdown table
    story.append(Paragraph("Framework Coverage", h2_style))
    fw_data = [["Framework", "Score", "Verified", "Total"]]
    for fw, data in result["framework_scores"].items():
        fw_data.append([fw, f"{data['score']}%", str(data["verified"]), str(data["total_controls"])])

    fw_table = Table(fw_data, colWidths=[2.5 * inch, inch, inch, inch])
    fw_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#1E5799")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF4FF")]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(fw_table)
    story.append(Spacer(1, 0.3 * inch))

    # Gaps table
    story.append(Paragraph("Identified Control Gaps", h2_style))
    if result["gaps"]:
        gap_data = [["Control", "Risk", "Frameworks", "Remediation"]]
        for g in result["gaps"][:15]:
            gap_data.append([
                g["control"][:35],
                g["risk"],
                ", ".join(g["frameworks"].keys()),
                g["remediation"][:50] + "...",
            ])
        gap_table = Table(gap_data, colWidths=[2.0 * inch, 0.6 * inch, 1.2 * inch, 2.5 * inch])
        gap_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#C0392B")),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFEEE E")]),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(gap_table)
    else:
        story.append(Paragraph("No critical gaps identified.", body_style))
    story.append(Spacer(1, 0.3 * inch))

    # Narrative report
    if result.get("narrative_report"):
        story.append(HRFlowable(color=colors.HexColor("#1E5799"), thickness=1))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("Executive Summary", h2_style))
        for para in result["narrative_report"].split("\n\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.1 * inch))

    # Footer
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(color=colors.HexColor("#CCCCCC"), thickness=0.5))
    story.append(Paragraph(
        "Generated by ProofLayer | AI-Powered Compliance Auditing | proooflayer.ai",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8,
                       textColor=colors.HexColor("#999999")),
    ))

    doc.build(story)


@app.get("/costs")
def get_costs():
    """Cost dashboard — shows per-model usage and savings vs. single-model approach."""
    return get_cost_summary()


@app.get("/audits")
def list_audits():
    """List all audits in session."""
    return {
        "audits": [
            {
                "audit_id":      v["audit_id"],
                "filename":      v.get("filename"),
                "overall_score": v["overall_score"],
                "risk_level":    v["risk_level"],
                "created":       v["created"],
            }
            for k, v in audit_store.items()
            if k.startswith("audit_") and "audit_id" in v
        ]
    }


# ── Serve frontend ────────────────────────────────────────────────────────────
frontend_path = pathlib.Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

    @app.get("/")
    def serve_frontend():
        return FileResponse(str(frontend_path / "index.html"))


# ── Entrypoint ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  ProofLayer - AI Compliance Engine")
    print("  Government Contractor Compliance Automation")
    print("="*55)
    print(f"\n  API:      http://localhost:8000")
    print(f"  Docs:     http://localhost:8000/docs")
    print(f"  UI:       http://localhost:8000/app\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
