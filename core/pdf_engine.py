"""
FTMS – PDF Engine
Generates Training Plan PDFs and Monthly Attendance Reports using ReportLab.
"""

from __future__ import annotations
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from core.logic import TrainingSession, Player


# ─── Colour palette ──────────────────────────────────────────────────────────
NEON_MINT    = colors.HexColor("#00FFCC")
ELECTRIC     = colors.HexColor("#00AAFF")
DARK_BG      = colors.HexColor("#0D1117")
DARK_CARD    = colors.HexColor("#161B22")
DARK_BORDER  = colors.HexColor("#21262D")
WHITE        = colors.white
LIGHT_GREY   = colors.HexColor("#8B949E")
RED          = colors.HexColor("#FF4444")
AMBER        = colors.HexColor("#FFB300")


def _get_exports_dir() -> Path:
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent
    exports = base / "exports"
    exports.mkdir(exist_ok=True)
    return exports


def _base_styles():
    styles = getSampleStyleSheet()
    return styles


def generate_training_plan_pdf(session: TrainingSession) -> str:
    """Generate A4 Training Plan PDF. Returns filepath."""
    filename = f"training_plan_{session.session_date}.pdf"
    filepath = str(_get_exports_dir() / filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=15*mm,  bottomMargin=15*mm,
    )

    styles = _base_styles()
    story = []

    # ── Header Banner ────────────────────────────────────────────────────────
    header_data = [[
        Paragraph(
            f'<font color="#00FFCC"><b>FTMS</b></font>'
            f'<font color="#8B949E"> · Football Training Management System</font>',
            ParagraphStyle("hdr", fontName="Helvetica-Bold", fontSize=14)
        ),
        Paragraph(
            f'<font color="#8B949E">Generated {datetime.now().strftime("%d %b %Y %H:%M")}</font>',
            ParagraphStyle("hdr_r", fontName="Helvetica", fontSize=9, alignment=TA_RIGHT)
        )
    ]]
    header_tbl = Table(header_data, colWidths=[120*mm, 50*mm])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), DARK_CARD),
        ("TEXTCOLOR",    (0,0), (-1,-1), WHITE),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[DARK_CARD]),
        ("BOX",          (0,0), (-1,-1), 1.5, NEON_MINT),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 6*mm))

    # ── Session Meta ─────────────────────────────────────────────────────────
    story.append(Paragraph(
        "TRAINING SESSION PLAN",
        ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=20,
                       textColor=WHITE, spaceAfter=2*mm)
    ))

    # Warning badge if high load
    if session.load_warning:
        story.append(Paragraph(
            "⚠  HIGH TRAINING LOAD — Consider reducing drill intensity",
            ParagraphStyle("warn", fontName="Helvetica-Bold", fontSize=10,
                           textColor=RED, backColor=colors.HexColor("#2D1515"),
                           borderPad=4, spaceAfter=3*mm)
        ))

    meta = [
        ["Date",     session.session_date],
        ["Start",    session.start_time],
        ["Duration", f"{session.total_duration} minutes"],
        ["Focus",    session.focus_area or "General"],
        ["Load",     f"{session.total_load} pts  (avg intensity {session.avg_intensity:.1f}/10)"],
        ["Drills",   str(len(session.drills))],
    ]
    meta_tbl = Table(meta, colWidths=[40*mm, 130*mm])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (0,-1), DARK_BORDER),
        ("BACKGROUND",   (1,0), (1,-1), DARK_CARD),
        ("TEXTCOLOR",    (0,0), (-1,-1), WHITE),
        ("TEXTCOLOR",    (0,0), (0,-1), NEON_MINT),
        ("FONTNAME",     (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",     (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[DARK_CARD, DARK_BG]*10),
        ("GRID",         (0,0), (-1,-1), 0.5, DARK_BORDER),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 6*mm))

    # ── Drill List ───────────────────────────────────────────────────────────
    story.append(Paragraph(
        "DRILL SCHEDULE",
        ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=13,
                       textColor=NEON_MINT, spaceAfter=3*mm)
    ))

    for idx, drill in enumerate(session.drills, 1):
        intensity_color = "#00FFCC" if drill.intensity <= 6 else ("#FFB300" if drill.intensity <= 8 else "#FF4444")
        drill_data = [
            [
                Paragraph(
                    f'<font color="#8B949E">{idx:02d}</font>  '
                    f'<b><font color="#FFFFFF">{drill.title}</font></b>',
                    ParagraphStyle("dt", fontName="Helvetica-Bold", fontSize=11)
                ),
                Paragraph(
                    f'<font color="{intensity_color}"><b>{drill.intensity}/10</b></font>'
                    f'<font color="#8B949E">  ·  {drill.duration_mins} min</font>',
                    ParagraphStyle("dm", fontName="Helvetica", fontSize=10, alignment=TA_RIGHT)
                ),
            ],
            [
                Paragraph(
                    f'<font color="#8B949E">{drill.description}</font>',
                    ParagraphStyle("dd", fontName="Helvetica", fontSize=9, leading=13)
                ),
                Paragraph(
                    f'<font color="#8B949E">{drill.category}</font>',
                    ParagraphStyle("dc", fontName="Helvetica", fontSize=9, alignment=TA_RIGHT)
                ),
            ]
        ]
        dtbl = Table(drill_data, colWidths=[120*mm, 50*mm])
        dtbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), DARK_CARD),
            ("BOX",          (0,0), (-1,-1), 0.8, DARK_BORDER),
            ("LINEBELOW",    (0,0), (-1,0),  0.5, DARK_BORDER),
            ("TOPPADDING",   (0,0), (-1,-1), 7),
            ("BOTTOMPADDING",(0,0), (-1,-1), 7),
            ("LEFTPADDING",  (0,0), (-1,-1), 10),
            ("RIGHTPADDING", (0,0), (-1,-1), 10),
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("SPAN",         (0,1), (0,1)),
        ]))
        story.append(KeepTogether([dtbl, Spacer(1, 3*mm)]))

    story.append(Spacer(1, 6*mm))

    # ── Notes ────────────────────────────────────────────────────────────────
    story.append(Paragraph(
        "COACH'S NOTES",
        ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=13,
                       textColor=NEON_MINT, spaceAfter=3*mm)
    ))
    notes_text = session.notes or "(No notes added)"
    notes_data = [[Paragraph(
        f'<font color="#C9D1D9">{notes_text}</font>',
        ParagraphStyle("nt", fontName="Helvetica", fontSize=10, leading=16)
    )]]
    # Empty lines for handwriting
    for _ in range(4):
        notes_data.append([
            Paragraph('<font color="#21262D">─────────────────────────────────────────────────────────────────────</font>',
                      ParagraphStyle("line", fontName="Helvetica", fontSize=9))
        ])
    notes_tbl = Table(notes_data, colWidths=[170*mm])
    notes_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), DARK_CARD),
        ("BOX",          (0,0), (-1,-1), 0.8, DARK_BORDER),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
    ]))
    story.append(notes_tbl)

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=DARK_BORDER))
    story.append(Paragraph(
        '<font color="#3D444D">FTMS · Football Training Management System · Confidential</font>',
        ParagraphStyle("footer", fontName="Helvetica", fontSize=8,
                       textColor=LIGHT_GREY, alignment=TA_CENTER)
    ))

    doc.build(story, onFirstPage=_dark_background, onLaterPages=_dark_background)
    return filepath


def generate_attendance_pdf(year: int, month: int, report_data: list) -> str:
    """Generate Monthly Attendance Report PDF."""
    import calendar
    month_name = calendar.month_name[month]
    filename = f"attendance_{year}_{month:02d}.pdf"
    filepath = str(_get_exports_dir() / filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm,  bottomMargin=15*mm,
    )
    story = []

    # Header
    story.append(Paragraph(
        f'<font color="#00FFCC"><b>FTMS</b></font>'
        f'<font color="#8B949E"> · Attendance Report — {month_name} {year}</font>',
        ParagraphStyle("hdr", fontName="Helvetica-Bold", fontSize=16,
                       textColor=WHITE, spaceAfter=6*mm)
    ))

    if not report_data:
        story.append(Paragraph(
            "No sessions recorded for this month.",
            ParagraphStyle("empty", fontName="Helvetica", fontSize=12, textColor=LIGHT_GREY)
        ))
    else:
        # Table header
        header = ["#", "Player", "Position", "Present", "Total", "Attendance %"]
        tbl_data = [header]
        for i, row in enumerate(report_data, 1):
            p   = row["player"]
            pct = row["pct"]
            pct_color = "#00FFCC" if pct >= 80 else ("#FFB300" if pct >= 60 else "#FF4444")
            tbl_data.append([
                str(i),
                p.name,
                p.position_full,
                str(row["present"]),
                str(row["total"]),
                f"{pct}%"
            ])

        # Compute dynamic column widths
        col_widths = [10*mm, 55*mm, 35*mm, 22*mm, 18*mm, 30*mm]
        tbl = Table(tbl_data, colWidths=col_widths, repeatRows=1)

        style = TableStyle([
            # Header row
            ("BACKGROUND",    (0,0), (-1,0), NEON_MINT),
            ("TEXTCOLOR",     (0,0), (-1,0), DARK_BG),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("ALIGN",         (0,0), (-1,-1), "CENTER"),
            ("ALIGN",         (1,1), (1,-1), "LEFT"),
            ("ALIGN",         (2,1), (2,-1), "LEFT"),
            # Body
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [DARK_CARD, DARK_BG]),
            ("TEXTCOLOR",      (0,1), (-1,-1), WHITE),
            ("GRID",           (0,0), (-1,-1), 0.4, DARK_BORDER),
            ("TOPPADDING",     (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",  (0,0), (-1,-1), 6),
            ("LEFTPADDING",    (0,0), (-1,-1), 6),
        ])

        # Colour the pct column per value
        for i, row in enumerate(report_data, 1):
            pct = row["pct"]
            if pct >= 80:
                c = NEON_MINT
            elif pct >= 60:
                c = AMBER
            else:
                c = RED
            style.add("TEXTCOLOR", (5, i), (5, i), c)
            style.add("FONTNAME",  (5, i), (5, i), "Helvetica-Bold")

        tbl.setStyle(style)
        story.append(tbl)
        story.append(Spacer(1, 8*mm))

        # Summary box
        avg = sum(r["pct"] for r in report_data) / len(report_data) if report_data else 0
        summary_data = [[
            Paragraph(f'<font color="#8B949E">Squad Average Attendance</font>',
                      ParagraphStyle("sl", fontName="Helvetica", fontSize=10)),
            Paragraph(f'<font color="#00FFCC"><b>{avg:.1f}%</b></font>',
                      ParagraphStyle("sr", fontName="Helvetica-Bold", fontSize=16, alignment=TA_RIGHT)),
        ]]
        stbl = Table(summary_data, colWidths=[120*mm, 50*mm])
        stbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), DARK_CARD),
            ("BOX",          (0,0), (-1,-1), 1.5, NEON_MINT),
            ("TOPPADDING",   (0,0), (-1,-1), 10),
            ("BOTTOMPADDING",(0,0), (-1,-1), 10),
            ("LEFTPADDING",  (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ]))
        story.append(stbl)

    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=DARK_BORDER))
    story.append(Paragraph(
        f'<font color="#3D444D">Generated {datetime.now().strftime("%d %b %Y %H:%M")} · FTMS Confidential</font>',
        ParagraphStyle("footer", fontName="Helvetica", fontSize=8, alignment=TA_CENTER)
    ))

    doc.build(story, onFirstPage=_dark_background, onLaterPages=_dark_background)
    return filepath


def _dark_background(canvas, doc):
    """Paint a dark background on every page."""
    canvas.saveState()
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.restoreState()


def open_print_dialog(filepath: str):
    """Trigger the OS print dialog for the given PDF."""
    if sys.platform == "win32":
        os.startfile(filepath, "print")
    elif sys.platform == "darwin":
        subprocess.run(["lpr", filepath])
    else:
        subprocess.run(["lpr", filepath])


def open_pdf(filepath: str):
    """Open PDF in default viewer."""
    if sys.platform == "win32":
        os.startfile(filepath)
    elif sys.platform == "darwin":
        subprocess.run(["open", filepath])
    else:
        subprocess.run(["xdg-open", filepath])
