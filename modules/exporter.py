from io import BytesIO
import re

from docx import Document

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    HRFlowable,
    ListFlowable,
    ListItem,
)

# --------------------------------------------------
# Markdown Helpers
# --------------------------------------------------

def clean_inline_markdown(text: str) -> str:
    """
    Convert inline Markdown into ReportLab-supported tags.
    """

    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)

    return text.strip()


# --------------------------------------------------
# PDF Export
# --------------------------------------------------

def export_pdf(summary: str) -> BytesIO:
    """
    Export Markdown notes as a properly formatted PDF.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER
    title_style.spaceAfter = 20

    heading1 = styles["Heading1"]
    heading1.spaceBefore = 16
    heading1.spaceAfter = 10

    heading2 = styles["Heading2"]
    heading2.spaceBefore = 12
    heading2.spaceAfter = 8

    body = styles["BodyText"]
    body.leading = 20
    body.spaceAfter = 8

    story = []

    lines = summary.splitlines()

    i = 0

    while i < len(lines):

        line = lines[i].rstrip()

        if not line:

            story.append(
                Spacer(1, 0.12 * inch)
            )

            i += 1
            continue

        # ------------------------------------------
        # Horizontal Rule
        # ------------------------------------------

        if line.strip() == "---":

            story.append(
                Spacer(1, 0.08 * inch)
            )

            story.append(
                HRFlowable(
                    width="100%",
                    color=colors.grey,
                    thickness=0.8,
                )
            )

            story.append(
                Spacer(1, 0.15 * inch)
            )

            i += 1
            continue

        # ------------------------------------------
        # Main Title
        # ------------------------------------------

        if line.startswith("# "):

            story.append(
                Paragraph(
                    clean_inline_markdown(line[2:]),
                    title_style,
                )
            )

            story.append(
                HRFlowable(
                    width="100%",
                    color=colors.black,
                    thickness=1,
                )
            )

            story.append(
                Spacer(1, 0.18 * inch)
            )

            i += 1
            continue

        # ------------------------------------------
        # Section Heading
        # ------------------------------------------

        if line.startswith("## "):

            story.append(
                Paragraph(
                    clean_inline_markdown(line[3:]),
                    heading1,
                )
            )

            i += 1
            continue

        # ------------------------------------------
        # Sub Heading
        # ------------------------------------------

        if line.startswith("### "):

            story.append(
                Paragraph(
                    clean_inline_markdown(line[4:]),
                    heading2,
                )
            )

            i += 1
            continue

        # ------------------------------------------
        # Bullet List
        # ------------------------------------------

        if line.startswith("- "):

            bullets = []

            while (
                i < len(lines)
                and lines[i].startswith("- ")
            ):

                bullets.append(
                    ListItem(
                        Paragraph(
                            clean_inline_markdown(lines[i][2:]),
                            body,
                        )
                    )
                )

                i += 1

            story.append(
                ListFlowable(
                    bullets,
                    bulletType="bullet",
                    leftIndent=18,
                )
            )

            story.append(
                Spacer(1, 0.08 * inch)
            )

            continue

        # ------------------------------------------
        # Normal Paragraph
        # ------------------------------------------

        story.append(
            Paragraph(
                clean_inline_markdown(line),
                body,
            )
        )

        i += 1

    document.build(story)

    buffer.seek(0)

    return buffer


# --------------------------------------------------
# Word Export
# --------------------------------------------------

def add_horizontal_line(document: Document):
    """
    Insert a horizontal separator.
    """
    paragraph = document.add_paragraph()
    run = paragraph.add_run("_" * 80)
    run.bold = False


def add_formatted_run(paragraph, text: str):
    """
    Add text while preserving simple Markdown.

    Supports:
    **bold**
    *italic*
    """

    pattern = r"(\*\*.*?\*\*|\*.*?\*)"

    parts = re.split(pattern, text)

    for part in parts:

        if not part:
            continue

        # Bold

        if part.startswith("**") and part.endswith("**"):

            run = paragraph.add_run(part[2:-2])
            run.bold = True

        # Italic

        elif part.startswith("*") and part.endswith("*"):

            run = paragraph.add_run(part[1:-1])
            run.italic = True

        else:

            paragraph.add_run(part)


def export_docx(summary: str) -> BytesIO:
    """
    Export Markdown notes as a formatted Word document.
    """

    document = Document()

    document.add_heading(
        "Lecture Notes",
        level=0,
    )

    lines = summary.splitlines()

    for line in lines:

        line = line.rstrip()

        if not line:
            document.add_paragraph()
            continue

        # -----------------------------------------
        # Horizontal Rule
        # -----------------------------------------

        if line.strip() == "---":

            add_horizontal_line(document)

            document.add_paragraph()

            continue

        # -----------------------------------------
        # Main Title
        # -----------------------------------------

        if line.startswith("# "):

            document.add_heading(
                line[2:],
                level=1,
            )

            add_horizontal_line(document)

            continue

        # -----------------------------------------
        # Section Heading
        # -----------------------------------------

        if line.startswith("## "):

            document.add_heading(
                line[3:],
                level=2,
            )

            continue

        # -----------------------------------------
        # Sub Heading
        # -----------------------------------------

        if line.startswith("### "):

            document.add_heading(
                line[4:],
                level=3,
            )

            continue

        # -----------------------------------------
        # Bullet List
        # -----------------------------------------

        if line.startswith("- "):

            paragraph = document.add_paragraph(
                style="List Bullet"
            )

            add_formatted_run(
                paragraph,
                line[2:],
            )

            continue

        # -----------------------------------------
        # Numbered List
        # -----------------------------------------

        if re.match(r"^\d+\.\s", line):

            text = re.sub(
                r"^\d+\.\s",
                "",
                line,
            )

            paragraph = document.add_paragraph(
                style="List Number"
            )

            add_formatted_run(
                paragraph,
                text,
            )

            continue

        # -----------------------------------------
        # Normal Paragraph
        # -----------------------------------------

        paragraph = document.add_paragraph()

        add_formatted_run(
            paragraph,
            line,
        )

        paragraph.paragraph_format.space_after = 8

    buffer = BytesIO()

    document.save(buffer)

    buffer.seek(0)

    return buffer