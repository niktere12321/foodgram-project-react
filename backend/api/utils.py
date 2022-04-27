import io
from typing import Dict, Union

from django.conf import settings
from django.http import FileResponse
from reportlab import rl_config
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FILE_NAME = 'Shopping_cart.pdf'
TITLE = 'Список покупок'


def pdf(data: Dict[int, Dict[str, Union[str, int]]]) -> FileResponse:

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/utils/fonts')
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    p.setFont('FreeSans', 15, leading=None)
    p.setFillColorRGB(0.29296875, 0.453125, 0.609375)
    p.drawString(260, 800, TITLE)
    p.line(0, 780, 1000, 780)
    p.line(0, 778, 1000, 778)
    x1 = 50
    y1 = 750
    o = 1
    for v in data.values():
        p.setFont('FreeSans', 15, leading=None)
        p.rect(x1 - 20, y1 - 12, 13, 13, fill=0)
        p.drawString(
            x1,
            y1 - 12,
            f"{o}. {v['name']} ({v['measurement_unit']}) - {v['amount']}"
        )
        y1 = y1 - 30
        o += 1
        if y1 == 30:
            y1 = 750
            p.showPage()
            p.setFont('FreeSans', 15, leading=None)
            p.setFillColorRGB(0.29296875, 0.453125, 0.609375)
            p.drawString(260, 800, TITLE)
            p.line(0, 780, 1000, 780)
            p.line(0, 778, 1000, 778)
            p.setTitle('SetTitle')
    p.setTitle('SetTitle')
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=FILE_NAME)
