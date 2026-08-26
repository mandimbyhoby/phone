from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph, KeepTogether,
)
from .models import Commande


ACCENT = colors.HexColor('#ffb224')
INK = colors.HexColor('#0d1017')
MUTED = colors.HexColor('#667085')
LIGHT = colors.HexColor('#f4f5f8')


def _format_amount(amount):
    return f'{amount:,.0f}'.replace(',', ' ') + ' Ar'


def _draw_logo(canvas, doc):
    logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'logo.svg'
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF
        logo = svg2rlg(str(logo_path))
        if logo:
            scale = 23 * mm / max(logo.width, logo.height)
            canvas.saveState()
            canvas.translate(doc.leftMargin, A4[1] - 31 * mm)
            canvas.scale(scale, scale)
            renderPDF.draw(logo, canvas, 0, 0)
            canvas.restoreState()
            return
    except Exception:
        pass

    canvas.saveState()
    canvas.setFillColor(ACCENT)
    canvas.circle(doc.leftMargin + 11 * mm, A4[1] - 20 * mm, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(INK)
    canvas.setFont('Helvetica-Bold', 15)
    canvas.drawCentredString(doc.leftMargin + 11 * mm, A4[1] - 25 * mm, 'PS')
    canvas.restoreState()


def generer_facture_pdf(commande):
    commande = Commande.objects.prefetch_related('lignes__produit').select_related('paiement').get(pk=commande.pk)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=40 * mm,
        bottomMargin=18 * mm,
        title=f'Facture commande {commande.id}',
        author='Phone Store',
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle('InvoiceTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, textColor=INK, alignment=TA_RIGHT, spaceAfter=4)
    subtitle = ParagraphStyle('InvoiceSubtitle', parent=styles['Normal'], fontSize=9, textColor=MUTED, alignment=TA_RIGHT)
    section = ParagraphStyle('Section', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=10, textColor=INK, spaceAfter=5)
    body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, leading=13, textColor=INK)
    small = ParagraphStyle('Small', parent=body, fontSize=8, textColor=MUTED)
    total_style = ParagraphStyle('Total', parent=body, fontName='Helvetica-Bold', fontSize=12, textColor=INK, alignment=TA_RIGHT)

    payment = getattr(commande, 'paiement', None)
    payment_label = payment.get_methode_display() if payment else 'Paiement en ligne'
    payment_reference = payment.reference if payment else '-'
    invoice_date = (payment.date_paiement if payment and payment.date_paiement else commande.date_commande) or timezone.now()

    story = [
        Table([
            [Paragraph('FACTURE', title), Paragraph(f'<b>Phone Store</b><br/>N° FAC-{commande.id:06d}<br/>{invoice_date:%d/%m/%Y}', subtitle)]
        ], colWidths=[100 * mm, 72 * mm], style=TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ])),
        Spacer(1, 13 * mm),
        Table([
            [Paragraph('<b>FACTUREE A</b>', section), Paragraph('<b>DETAILS DU PAIEMENT</b>', section)],
            [Paragraph(f'<b>{escape(commande.nom)}</b><br/>{escape(commande.email)}<br/>{escape(commande.telephone)}<br/>{escape(commande.adresse)}<br/>{escape(commande.ville)}', body),
             Paragraph(f'Methode : {payment_label}<br/>Reference : {payment_reference}<br/>Statut : Paiement confirme', body)]
        ], colWidths=[86 * mm, 86 * mm], style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e3e6ec')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e3e6ec')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 9),
            ('RIGHTPADDING', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])),
        Spacer(1, 12 * mm),
    ]

    rows = [[Paragraph('<b>ARTICLE</b>', small), Paragraph('<b>QTE</b>', small), Paragraph('<b>PRIX UNITAIRE</b>', small), Paragraph('<b>TOTAL</b>', small)]]
    for ligne in commande.lignes.all():
        rows.append([
            Paragraph(escape(ligne.produit.nom), body),
            str(ligne.quantite),
            _format_amount(ligne.prix_unitaire),
            _format_amount(ligne.sous_total),
        ])
    rows.append(['', '', Paragraph('<b>TOTAL A PAYER</b>', body), Paragraph(_format_amount(commande.total), total_style)])
    table = Table(rows, colWidths=[82 * mm, 18 * mm, 36 * mm, 36 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), INK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#e3e6ec')),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('SPAN', (0, -1), (1, -1)),
        ('BACKGROUND', (0, -1), (-1, -1), ACCENT),
        ('LINEABOVE', (0, -1), (-1, -1), 1, ACCENT),
    ]))
    story.extend([table, Spacer(1, 15 * mm), KeepTogether([
        Paragraph('Merci pour votre confiance.', section),
        Paragraph('Cette facture est disponible dans votre espace client. Pour toute question, contactez-nous en indiquant le numero de commande.', small),
    ])])
    doc.build(story, onFirstPage=_draw_logo)
    return buffer.getvalue()


def envoyer_facture(commande):
    pdf = generer_facture_pdf(commande)
    email = EmailMessage(
        subject=f'Commande #{commande.id} - Votre facture Phone Store',
        body=(
            f'Bonjour {commande.nom},\n\n'
            f'Votre paiement pour la commande #{commande.id} est confirme.\n'
            'Vous trouverez votre facture en PDF en piece jointe. '
            'Elle reste aussi telechargeable depuis votre profil.\n\n'
            'Merci pour votre confiance.\nPhone Store'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[commande.email],
    )
    email.attach(f'facture-commande-{commande.id}.pdf', pdf, 'application/pdf')
    email.send(fail_silently=False)


def envoyer_email_annulation(commande):
    email = EmailMessage(
        subject=f'Commande #{commande.id} annulee - Phone Store',
        body=(
            f'Bonjour {commande.nom},\n\n'
            f'Votre commande #{commande.id} a bien ete annulee.\n'
            'Aucun paiement ne sera conserve pour cette commande. '
            'Le stock des articles a ete remis a jour.\n\n'
            'Si cette annulation est une erreur, contactez-nous en indiquant '
            f'la commande #{commande.id}.\n\n'
            'Cordialement,\nPhone Store'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[commande.email],
    )
    email.send(fail_silently=False)
