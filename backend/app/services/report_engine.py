import csv
import io
import json
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def _flatten_record(image, material, waste, recyclability, recommendation) -> Dict[str, Any]:
    return {
        "image_id": image.id,
        "filename": image.filename,
        "created_at": image.created_at.isoformat() if image.created_at else None,
        "fabric_texture": image.fabric_texture,
        "fabric_pattern": image.fabric_pattern,
        "fabric_confidence_score": image.fabric_confidence_score,
        "image_quality_score": image.image_quality_score,
        "damage_detected": image.damage_detected,
        "damage_level": image.damage_level,
        "contamination_detected": image.contamination_detected,
        "contamination_percentage": image.contamination_percentage,
        "material_name": material.material_name if material else None,
        "fabric_category": material.fabric_category if material else None,
        "fiber_composition": material.fiber_composition if material else None,
        "fabric_quality": material.fabric_quality if material else None,
        "material_confidence_percentage": material.material_confidence_percentage if material else None,
        "sustainability_score": material.sustainability_score if material else None,
        "waste_category": waste.waste_category if waste else None,
        "waste_condition": waste.waste_condition if waste else None,
        "recyclability_percentage": waste.recyclability_percentage if waste else None,
        "disposal_method": waste.disposal_method if waste else None,
        "reuse_potential": recyclability.reuse_potential if recyclability else None,
        "repairability_score": recyclability.repairability_score if recyclability else None,
        "disposal_recommendation": recyclability.disposal_recommendation if recyclability else None,
        "best_recycling_method": recommendation.best_recycling_method if recommendation else None,
        "environmental_impact_score": recommendation.environmental_impact_score if recommendation else None,
        "reuse_suggestions": recommendation.reuse_suggestions if recommendation else None,
        "waste_reduction_strategies": recommendation.waste_reduction_strategies if recommendation else None,
    }


def generate_json_report(image, material, waste, recyclability, recommendation) -> bytes:
    data = _flatten_record(image, material, waste, recyclability, recommendation)
    return json.dumps(data, indent=2, default=str).encode("utf-8")


def generate_csv_report(image, material, waste, recyclability, recommendation) -> bytes:
    data = _flatten_record(image, material, waste, recyclability, recommendation)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Field", "Value"])
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        writer.writerow([key, value])
    return buffer.getvalue().encode("utf-8")


def generate_pdf_report(image, material, waste, recyclability, recommendation) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], textColor=colors.HexColor("#0f172a"), spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        "HeadingCustom", parent=styles["Heading2"], textColor=colors.HexColor("#0d9488"),
        spaceBefore=14, spaceAfter=8,
    )
    normal = styles["Normal"]

    story = []
    story.append(Paragraph("Textile Waste Intelligence Platform", title_style))
    story.append(Paragraph("Material Recognition & Waste Classification Report", styles["Heading3"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} &nbsp;|&nbsp; Image ID: {image.id}",
        normal,
    ))
    story.append(Spacer(1, 14))

    def table_from_rows(rows):
        t = Table(rows, colWidths=[2.3 * inch, 4.0 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0fdfa")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        return t

    story.append(Paragraph("Image Analysis", heading_style))
    story.append(table_from_rows([
        ["Filename", image.filename],
        ["Fabric Texture", image.fabric_texture or "-"],
        ["Fabric Pattern", image.fabric_pattern or "-"],
        ["Fabric Confidence", f"{image.fabric_confidence_score}%"],
        ["Image Quality Score", f"{image.image_quality_score}/100"],
        ["Damage Detected", "Yes" if image.damage_detected else "No"],
        ["Contamination Detected", "Yes" if image.contamination_detected else "No"],
        ["Contamination %", f"{image.contamination_percentage}%"],
    ]))

    if material:
        story.append(Paragraph("Material Classification", heading_style))
        composition = ", ".join(f"{k}: {v}%" for k, v in (material.fiber_composition or {}).items())
        story.append(table_from_rows([
            ["Material", material.material_name],
            ["Fabric Category", material.fabric_category or "-"],
            ["Fiber Composition", composition or "-"],
            ["Fabric Quality", material.fabric_quality or "-"],
            ["Confidence", f"{material.material_confidence_percentage}%"],
            ["Sustainability Score", f"{material.sustainability_score}/100"],
        ]))

    if waste:
        story.append(Paragraph("Waste Classification", heading_style))
        story.append(table_from_rows([
            ["Waste Category", waste.waste_category],
            ["Condition", waste.waste_condition or "-"],
            ["Recyclability %", f"{waste.recyclability_percentage}%"],
            ["Disposal Method", waste.disposal_method or "-"],
        ]))

    if recyclability:
        story.append(Paragraph("Recyclability Assessment", heading_style))
        story.append(table_from_rows([
            ["Recyclability %", f"{recyclability.recyclability_percentage}%"],
            ["Reuse Potential", f"{recyclability.reuse_potential}/100"],
            ["Repairability Score", f"{recyclability.repairability_score}/100"],
            ["Recommendation", recyclability.disposal_recommendation or "-"],
        ]))

    if recommendation:
        story.append(Paragraph("Recycling Recommendation", heading_style))
        story.append(table_from_rows([
            ["Best Method", recommendation.best_recycling_method],
            ["Sustainability Score", f"{recommendation.sustainability_score}/100"],
            ["Environmental Impact", f"{recommendation.environmental_impact_score}/100"],
        ]))
        if recommendation.reuse_suggestions:
            story.append(Spacer(1, 6))
            story.append(Paragraph("Reuse Suggestions:", styles["Heading4"]))
            for s in recommendation.reuse_suggestions:
                story.append(Paragraph(f"&bull; {s}", normal))
        if recommendation.waste_reduction_strategies:
            story.append(Spacer(1, 6))
            story.append(Paragraph("Waste Reduction Strategies:", styles["Heading4"]))
            for s in recommendation.waste_reduction_strategies:
                story.append(Paragraph(f"&bull; {s}", normal))

    doc.build(story)
    return buffer.getvalue()
