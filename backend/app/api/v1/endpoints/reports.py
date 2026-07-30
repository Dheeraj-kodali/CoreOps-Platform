import csv
import io
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.repositories.visitor_repository import VisitorRepository

router = APIRouter()


@router.get("/export")
async def export_reports(
    export_format: str = Query(..., alias="format", pattern="^(csv|excel|pdf)$"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    purpose_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visitor_repo = VisitorRepository(db)
    visitors, _ = await visitor_repo.search_and_filter(
        date_from=date_from,
        date_to=date_to,
        purpose_id=purpose_id,
        limit=10000,
    )

    if export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "UUID", "Name", "Phone", "Gender", "Age", "Persons", "Purpose", "Date", "Time", "Volunteer"])

        for v in visitors:
            writer.writerow([
                v.id,
                v.visitor_uuid,
                v.name,
                v.phone_number,
                v.gender,
                v.age,
                v.persons_count,
                v.purpose.name_en if v.purpose else "",
                str(v.visitor_date),
                str(v.visitor_time),
                v.volunteer_id,
            ])

        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=visitor_report_{date.today()}.csv"},
        )

    elif export_format == "excel":
        # Simplified openpyxl generation
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Visitors Report"

        ws.append(["ID", "UUID", "Name", "Phone", "Gender", "Age", "Persons", "Purpose", "Date", "Time", "Volunteer"])
        for v in visitors:
            ws.append([
                v.id,
                v.visitor_uuid,
                v.name,
                v.phone_number,
                v.gender,
                v.age,
                v.persons_count,
                v.purpose.name_en if v.purpose else "",
                str(v.visitor_date),
                str(v.visitor_time),
                v.volunteer_id,
            ])

        excel_stream = io.BytesIO()
        wb.save(excel_stream)
        excel_stream.seek(0)

        return StreamingResponse(
            excel_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=visitor_report_{date.today()}.xlsx"},
        )

    elif export_format == "pdf":
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        pdf_stream = io.BytesIO()
        c = canvas.Canvas(pdf_stream, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "Sri Kalki Seva Alayam - Visitor Management System")
        c.setFont("Helvetica", 12)
        c.drawString(50, 730, f"Generated Report - {date.today()}")
        c.line(50, 720, 550, 720)

        y = 690
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Name")
        c.drawString(200, y, "Phone")
        c.drawString(320, y, "Gender/Age")
        c.drawString(420, y, "Purpose")
        c.drawString(500, y, "Date")
        y -= 20
        c.setFont("Helvetica", 9)

        for v in visitors[:30]:  # First page slice
            c.drawString(50, y, v.name[:22])
            c.drawString(200, y, v.phone_number)
            c.drawString(320, y, f"{v.gender}/{v.age}")
            c.drawString(420, y, (v.purpose.name_en if v.purpose else "")[:12])
            c.drawString(500, y, str(v.visitor_date))
            y -= 18

        c.showPage()
        c.save()
        pdf_stream.seek(0)

        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=visitor_report_{date.today()}.pdf"},
        )
