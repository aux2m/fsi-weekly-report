#!/usr/bin/env python3
"""
Bennett-Kew P-8 Academy - Weekly Construction Progress Report Generator (r1)
=============================================================================
Generates a branded PDF report matching the FSI template revision 1 exactly.

CORRECTIONS FROM R1:
  - Banner: removed curly braces from report number
  - Project Report Details: 2-column layout (dates left, GC/CM right)
  - Activities/Milestones/Critical Items: wider 2-line fields per bullet
  - Planned Activities & Special Considerations: full-width lines

Usage:
  python generate_report.py                      # Generate with sample data
  python generate_report.py data.json            # Generate from JSON data
  python generate_report.py --output report.pdf  # Specify output filename
"""

import sys
import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from textwrap import wrap

# ============================================================================
# COLOR PALETTE
# ============================================================================
DARK_BLUE = HexColor('#1B2A4A')
GREEN_BANNER = HexColor('#4CAF50')
DARK_GREEN = HexColor('#2E7D32')
NAVY = HexColor('#1A237E')
RED_BANNER = HexColor('#D32F2F')
LIGHT_GRAY = HexColor('#F5F5F5')
MED_GRAY = HexColor('#9E9E9E')
DARK_GRAY = HexColor('#424242')
WHITE = white
BLACK = black
BLUE_LINK = HexColor('#1565C0')

PAGE_W, PAGE_H = letter
MARGIN_L = 20
MARGIN_R = 20
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

SAMPLE_DATA = {
    "report_number": "03",
    "report_week": "02/03—02/07",
    "issued_date": "Friday, February 7, 2025",
    "project_name": "Bennett-Kew P-8 Academy",
    "project_subtitle": "New Classroom Building Project",
    "project_address": "11710 S Cherry Ave, Inglewood, CA 90303",
    "architect": "HED Design",
    "project_duration": "September 2025 - September 2026",
    "prepared_by": "Adam Wentworth, PM",
    "general_contractor": "PCN3, Inc.",
    "construction_manager": "Fonder-Salari, Inc.",
    "district": "Inglewood Unified School District",
    "project_description": (
        "The project generally consists of the construction of: a single story building "
        "consisting of 6 classrooms, restrooms, utility spaces and a large multipurpose "
        "space. Site work includes new asphalt play field, courts, solar installation, "
        "fire lane striping and modifications to fencing. Play structures and soft surface "
        "materials are owner furnished, contractor coordinated and installed along with "
        "minor landscaping. Project is on an active school site, all work will be "
        "coordinated with the District to cause the least disruption to class, "
        "particularly for special education programming."
    ),
    "countdown_days": "347",
    "phase": "Foundations & Underground",
    "overall_progress": "8",
    "schedule_status": "On Schedule",
    "activities_completed": [
        "Completed footing excavation Grid Lines 1-10",
        "Poured continuous footings at Grid A & B",
        "Underground plumbing rough-in for restrooms",
        "Installed erosion control measures per SWPPP",
        "Electrical conduit placement in slab area",
    ],
    "milestones_achieved": [
        "Foundation inspection passed (DSA)",
        "Underground plumbing inspection cleared",
        "Site grading approval received from City",
    ],
    "critical_items": [
        "Awaiting RFI #012 response from HED Design re: footing depth at Grid 7",
    ],
    "week1_dates": "02/10—02/14",
    "week1_level": "MODERATE",
    "week1_activities": ["Stem wall forming", "Concrete pours", "Rebar installation"],
    "week2_dates": "02/17—02/21",
    "week2_level": "MODERATE",
    "week2_activities": ["SOG prep work", "Underground MEP", "Form stripping"],
    "week3_dates": "02/24—02/28",
    "week3_level": "MODERATE",
    "week3_activities": ["SOG concrete pour", "Pump truck on site", "Increased traffic"],
    "planned_activities": [
        "Form and pour stem walls Grid Lines 1-5",
        "Continue underground electrical conduit",
        "Install anchor bolts per structural plans",
        "Begin SOG gravel base preparation",
    ],
    "noise_index": "Moderate",
    "noise_level": "3/5",
    "special_considerations": [
        "Concrete pump truck Tuesday AM - temporary parking impact",
        "Coordinate with after-school program for safe walkway access",
    ],
    "photo_captions": [
        "Marking new classroom building foundation",
        "Erosion control protecting site during rain",
        "SOG concrete pour Grid 11-15",
        "Post-pour sawcut & curing operations",
    ],
    "commitment_text": (
        "Our construction team completed this week's activities with zero educational "
        "disruptions while maintaining the highest safety standards. Moving into "
        "higher-impact phases, we remain committed to advance communication, flexible "
        "scheduling around special programs, and immediate response to any campus concerns."
    ),
    "contact_name": "Adam Wentworth, Construction Manager",
    "contact_phone": "(661) 204-1154",
    "contact_email": "adam.wentworth@fonder-salari.com",
    "logo_fs": "fs_logo.png",
    "logo_bk": "bk_logo.jpg",
    "logo_iusd": "iusd_logo.jpg",
    "photos": ["photo1.jpg", "photo2.jpg", "photo3.jpg", "photo4.jpg", "photo5.jpg", "photo6.jpg"],
}


def safe_image(c, path, x, y, w, h):
    if os.path.exists(path):
        try:
            c.drawImage(path, x, y, w, h, preserveAspectRatio=True, mask='auto')
        except Exception:
            c.setStrokeColor(MED_GRAY); c.setFillColor(LIGHT_GRAY)
            c.rect(x, y, w, h, fill=1, stroke=1)
    else:
        c.setStrokeColor(MED_GRAY); c.setFillColor(LIGHT_GRAY)
        c.rect(x, y, w, h, fill=1, stroke=1)
        c.setFillColor(MED_GRAY); c.setFont("Helvetica", 6)
        c.drawCentredString(x + w/2, y + h/2, f"[{os.path.basename(path)}]")


def draw_bullet_list(c, items, x, y, max_width, font_name, font_size, color=BLACK, leading=None):
    if leading is None:
        leading = font_size + 3
    current_y = y
    indent = 10
    chars = max(20, int((max_width - indent) / (font_size * 0.48)))
    for item in items:
        c.setFont(font_name, font_size); c.setFillColor(color)
        c.drawString(x, current_y, "•")
        for i, line in enumerate(wrap(item, width=chars)):
            c.drawString(x + indent, current_y, line)
            if i < len(wrap(item, width=chars)) - 1:
                current_y -= leading
        current_y -= leading
    return current_y


def generate_report(data, output_path="Weekly_Progress_Report.pdf"):
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setTitle(f"Weekly Progress Report #{data['report_number']} - {data['project_name']}")
    c.setAuthor(data['prepared_by'])
    y = PAGE_H

    # ── HEADER ──────────────────────────────────────────────────────────
    header_h = 78
    y -= header_h + 8
    safe_image(c, data.get('logo_fs', ''), MARGIN_L, y, 75, header_h)

    c.setFont("Helvetica-Bold", 14); c.setFillColor(DARK_BLUE)
    c.drawCentredString(PAGE_W/2, y + header_h - 20, data['project_name'])
    c.setFont("Helvetica-Bold", 11); c.setFillColor(BLACK)
    c.drawCentredString(PAGE_W/2, y + header_h - 38, data['project_subtitle'])
    c.setFont("Helvetica-Bold", 8); c.setFillColor(DARK_GREEN)
    c.drawCentredString(PAGE_W/2, y + header_h - 52, f"Project Address: {data['project_address']}")

    logo_rx = PAGE_W - MARGIN_R - 105
    safe_image(c, data.get('logo_bk', ''), logo_rx, y + header_h/2, 48, header_h/2)
    safe_image(c, data.get('logo_iusd', ''), logo_rx + 52, y, 53, header_h)

    # ── GREEN BANNER (no curly braces per r1) ───────────────────────────
    y -= 4
    bh = 22
    c.setFillColor(GREEN_BANNER)
    c.rect(MARGIN_L, y - bh, CONTENT_W, bh, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 13); c.setFillColor(WHITE)
    c.drawCentredString(PAGE_W/2, y - bh + 6,
                        f"WEEKLY CONSTRUCTION PROGRESS REPORT {data['report_number']}")
    y -= bh

    # ── ARCHITECT INFO + DESCRIPTION ────────────────────────────────────
    y -= 2
    info_h = 90; info_lw = 130
    lx = MARGIN_L + 4; ly = y - 12
    for label, val, bold_val in [
        ("Architect:", data['architect'], True),
        ("Project Duration:", data['project_duration'], True),
        ("Prepared by:", data['prepared_by'], True),
    ]:
        c.setFont("Helvetica" + ("-Bold" if ":" in label else ""), 8); c.setFillColor(BLACK)
        c.drawString(lx, ly, label); ly -= 11
        c.setFont("Helvetica-BoldOblique", 8); c.setFillColor(DARK_GREEN)
        c.drawString(lx, ly, val); ly -= 12

    desc_x = MARGIN_L + info_lw + 5
    desc_w = CONTENT_W - info_lw - 10
    c.setFont("Helvetica-Bold", 13); c.setFillColor(DARK_GREEN)
    c.drawCentredString(desc_x + desc_w/2, y - 14, "PROJECT DESCRIPTION")
    c.setStrokeColor(MED_GRAY); c.setLineWidth(0.5)
    c.rect(desc_x, y - info_h, desc_w, info_h - 18, stroke=1, fill=0)
    dy = y - 28
    c.setFont("Helvetica", 6.5); c.setFillColor(BLACK)
    for line in wrap(data['project_description'], width=int((desc_w-8)/(6.5*0.47))):
        c.drawString(desc_x + 4, dy, line); dy -= 8.5
    y -= info_h + 2

    # ── PROJECT REPORT DETAILS / COUNTDOWN BANNERS ──────────────────────
    bh2 = 18; left_bw = CONTENT_W * 0.58; right_bw = CONTENT_W - left_bw
    c.setFillColor(NAVY)
    c.rect(MARGIN_L, y - bh2, left_bw, bh2, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 11); c.setFillColor(WHITE)
    c.drawCentredString(MARGIN_L + left_bw/2, y - bh2 + 5, "PROJECT REPORT DETAILS")
    c.setFillColor(DARK_GREEN)
    c.rect(MARGIN_L + left_bw, y - bh2, right_bw, bh2, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9); c.setFillColor(WHITE)
    c.drawCentredString(MARGIN_L + left_bw + right_bw/2, y - bh2 + 5, "Substantial Completion Countdown")
    y -= bh2

    # ── DETAILS BOX (r1: 2-column layout) ───────────────────────────────
    dh = 32
    c.setStrokeColor(MED_GRAY); c.setLineWidth(0.5)
    c.rect(MARGIN_L, y - dh, left_bw, dh, stroke=1, fill=0)
    dx = MARGIN_L + 6; half = left_bw / 2

    # Left: dates
    dy = y - 12
    c.setFont("Helvetica-Bold", 8); c.setFillColor(BLACK)
    c.drawString(dx, dy, "Report Week: "); c.setFont("Helvetica", 8)
    c.drawString(dx + 70, dy, data['report_week'])
    dy -= 12
    c.setFont("Helvetica-Bold", 8); c.setFillColor(BLACK)
    c.drawString(dx, dy, "Issued: "); c.setFont("Helvetica", 8)
    c.drawString(dx + 40, dy, data['issued_date'])

    # Right: GC/CM
    rx = MARGIN_L + half + 10; dy = y - 12
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(rx, dy, "General Contractor: "); c.setFont("Helvetica", 7.5)
    c.drawString(rx + 95, dy, data['general_contractor'])
    dy -= 12
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(rx, dy, "Construction Manager: ")
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(DARK_GREEN)
    c.drawString(rx + 105, dy, data['construction_manager'])

    # Countdown box
    cx = MARGIN_L + left_bw
    c.setFillColor(LIGHT_GRAY)
    c.rect(cx, y - dh, right_bw, dh, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 26); c.setFillColor(RED_BANNER)
    c.drawCentredString(cx + right_bw/2 - 30, y - dh + 6, data['countdown_days'])
    c.setFont("Helvetica-Bold", 11); c.setFillColor(DARK_BLUE)
    c.drawString(cx + right_bw/2, y - dh + 10, "Calendar Days")
    y -= dh

    # ── ACTIVITIES + IMPACT BANNERS ─────────────────────────────────────
    y -= 2; abh = 18
    left_col = CONTENT_W * 0.55; right_col = CONTENT_W - left_col
    right_x = MARGIN_L + left_col + 2; impact_w = right_col - 2

    c.setFillColor(GREEN_BANNER)
    c.rect(MARGIN_L, y - abh, left_col, abh, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 11); c.setFillColor(WHITE)
    c.drawCentredString(MARGIN_L + left_col/2, y - abh + 5, "THIS WEEK'S COMPLETED ACTIVITIES")
    c.setFillColor(RED_BANNER)
    c.rect(right_x, y - abh, impact_w, abh, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9); c.setFillColor(WHITE)
    c.drawCentredString(right_x + impact_w/2, y - abh + 5, "3-WEEK CONSTRUCTION IMPACT")
    y -= abh

    # ── MAIN CONTENT ────────────────────────────────────────────────────
    main_h = 195
    c.setStrokeColor(MED_GRAY)
    c.rect(MARGIN_L, y - main_h, left_col, main_h, stroke=1, fill=0)

    lx = MARGIN_L + 6; ly = y - 11; act_w = left_col/2 - 8
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(lx, ly, "Phase: "); c.setFont("Helvetica", 7.5)
    c.drawString(lx + 32, ly, data['phase']); ly -= 10
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(lx, ly, "Overall Progress: "); c.setFont("Helvetica", 7.5)
    c.drawString(lx + 78, ly, f"{data['overall_progress']}% Complete"); ly -= 10
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(lx, ly, "Schedule Status: "); c.setFont("Helvetica", 7.5)
    c.drawString(lx + 73, ly, data['schedule_status']); ly -= 12

    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(lx, ly, "Activities Completed:"); ly -= 10
    ly = draw_bullet_list(c, data['activities_completed'], lx, ly, act_w, "Helvetica", 6.5, BLACK, 9)

    mx = MARGIN_L + left_col/2 + 5; my = y - 11
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(mx, my, "Milestones Achieved:"); my -= 10
    my = draw_bullet_list(c, data['milestones_achieved'], mx, my, act_w, "Helvetica", 6.5, BLACK, 9)
    my -= 8
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(mx, my, "Critical Items:"); my -= 10
    draw_bullet_list(c, data['critical_items'], mx, my, act_w, "Helvetica", 6.5, RED_BANNER, 9)

    # Impact grid
    col_w = impact_w / 3
    for i, (dk, lk, ak) in enumerate([
        ("week1_dates", "week1_level", "week1_activities"),
        ("week2_dates", "week2_level", "week2_activities"),
        ("week3_dates", "week3_level", "week3_activities"),
    ]):
        gx = right_x + i * col_w; gy = y
        c.setFont("Helvetica-Bold", 7); c.setFillColor(BLACK)
        c.drawCentredString(gx + col_w/2, gy - 10, f"Week {i+1}")
        c.setFont("Helvetica", 5.5); c.setFillColor(MED_GRAY)
        c.drawCentredString(gx + col_w/2, gy - 19, f"({data[dk]})")
        level = data[lk]
        bc = {"LOW": HexColor('#4CAF50'), "MODERATE": HexColor('#FF9800'), "HIGH": HexColor('#E53935')}
        bw = col_w - 8; bx = gx + 4; by = gy - 35
        c.setFillColor(bc.get(level.upper(), HexColor('#FF9800')))
        c.roundRect(bx, by, bw, 14, 2, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 7); c.setFillColor(WHITE)
        c.drawCentredString(bx + bw/2, by + 4, level.upper())
        ay = by - 10
        for act in data[ak][:3]:
            c.setFont("Helvetica", 5.5); c.setFillColor(DARK_GRAY)
            c.drawCentredString(gx + col_w/2, ay, act[:22] + ("..." if len(act) > 22 else ""))
            ay -= 8

    # Photos (right column)
    photos = data.get('photos', []); captions = data.get('photo_captions', [])
    pw = impact_w - 4; ph = 50; psy = y - 80
    for i in range(min(2, len(photos))):
        py = psy - i * (ph + 4)
        if py - ph < y - main_h: break
        safe_image(c, photos[i], right_x + 2, py - ph, pw, ph)
        if i < len(captions):
            c.setFillColor(HexColor('#00000088'))
            c.rect(right_x + 2, py - ph, pw, 10, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 5.5); c.setFillColor(WHITE)
            c.drawString(right_x + 5, py - ph + 3, captions[i])
    y -= main_h + 2

    # ── NEXT WEEK BANNER ────────────────────────────────────────────────
    nbh = 18
    c.setFillColor(GREEN_BANNER)
    c.rect(MARGIN_L, y - nbh, CONTENT_W, nbh, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 12); c.setFillColor(WHITE)
    c.drawCentredString(PAGE_W/2, y - nbh + 4, "NEXT WEEK ACTIVITY PROJECTION")
    y -= nbh

    # ── NEXT WEEK CONTENT ───────────────────────────────────────────────
    nh = 155
    c.setStrokeColor(MED_GRAY)
    c.rect(MARGIN_L, y - nh, left_col, nh, stroke=1, fill=0)
    lx = MARGIN_L + 6; ly = y - 12
    c.setFont("Helvetica-Bold", 8); c.setFillColor(BLACK)
    c.drawString(lx, ly, "PLANNED ACTIVITIES"); ly -= 11
    ly = draw_bullet_list(c, data['planned_activities'], lx, ly, left_col - 15, "Helvetica", 7, BLACK, 11)
    ly -= 6
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(lx, ly, "ANTICIPATED IMPACT LEVELS"); ly -= 12
    c.setFont("Helvetica-Bold", 7); c.setFillColor(BLACK)
    c.drawString(lx, ly, "NOISE INDEX: "); c.setFont("Helvetica", 7)
    c.drawString(lx + 68, ly, f"{data['noise_index']}  (Level {data['noise_level']})"); ly -= 10
    c.setFont("Helvetica", 6.5)
    c.drawString(lx, ly, "Peak Impact Times: Mon-Fri 7:00 AM - 3:00 PM"); ly -= 14
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(lx, ly, "SPECIAL CONSIDERATIONS"); ly -= 10
    draw_bullet_list(c, data['special_considerations'], lx, ly, left_col - 15, "Helvetica", 6.5, BLACK, 9)

    # More photos
    if len(photos) > 2:
        ph2 = 70
        for i in range(min(2, len(photos) - 2)):
            idx = i + 2; py = y - 5 - i * (ph2 + 5)
            safe_image(c, photos[idx], right_x + 2, py - ph2, pw, ph2)
            if idx < len(captions):
                c.setFillColor(HexColor('#00000088'))
                c.rect(right_x + 2, py - ph2, pw, 10, fill=1, stroke=0)
                c.setFont("Helvetica-Bold", 5.5); c.setFillColor(WHITE)
                c.drawString(right_x + 5, py - ph2 + 3, captions[idx])
    y -= nh + 2

    # ── COMMITMENT ──────────────────────────────────────────────────────
    cbh = 22
    c.setFillColor(DARK_BLUE)
    c.rect(MARGIN_L, y - cbh, CONTENT_W, cbh, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 14); c.setFillColor(WHITE)
    c.drawString(MARGIN_L + 10, y - cbh + 6, "COMMITMENT")
    y -= cbh

    ch = 65
    c.setStrokeColor(MED_GRAY)
    c.rect(MARGIN_L, y - ch, CONTENT_W, ch, stroke=1, fill=0)
    cx_t = MARGIN_L + 8; cy_t = y - 12
    full = f"Community Promise: {data['commitment_text']}"
    cpl = int((CONTENT_W - 20) / (7 * 0.46))
    for line in wrap(full, width=cpl):
        if line.startswith("Community Promise:"):
            c.setFont("Helvetica-Bold", 7); c.setFillColor(BLACK)
            c.drawString(cx_t, cy_t, "Community Promise: ")
            c.setFont("Helvetica", 7)
            c.drawString(cx_t + 88, cy_t, line[len("Community Promise: "):])
        else:
            c.setFont("Helvetica", 7); c.setFillColor(BLACK)
            c.drawString(cx_t, cy_t, line)
        cy_t -= 9
    cy_t -= 2
    c.setFont("Helvetica-Bold", 7.5); c.setFillColor(BLACK)
    c.drawString(cx_t, cy_t, "Direct Contact for Immediate Issues:"); cy_t -= 10
    c.setFont("Helvetica-Bold", 7)
    c.drawString(cx_t, cy_t, f"{data['contact_name']} {data['contact_phone']} | ")
    c.setFont("Helvetica", 7); c.setFillColor(BLUE_LINK)
    c.drawString(cx_t + len(f"{data['contact_name']} {data['contact_phone']} | ") * 3.5, cy_t, data['contact_email'])

    cy_t -= 14
    c.setFont("Helvetica-BoldOblique", 9); c.setFillColor(NAVY)
    c.drawCentredString(PAGE_W/2, cy_t, data['district'])

    c.save()
    return output_path


if __name__ == "__main__":
    output = "Weekly_Progress_Report.pdf"
    data = SAMPLE_DATA
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--output" and i < len(sys.argv) - 1:
            output = sys.argv[i + 1]
        elif arg.endswith('.json'):
            with open(arg) as f:
                data = {**SAMPLE_DATA, **json.load(f)}
    print(f"✅ Report generated: {generate_report(data, output)}")
