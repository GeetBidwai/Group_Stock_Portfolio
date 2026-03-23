import io

from apps.sentiment_module.services.sentiment_service import SentimentAggregationService


class SentimentReportService:
    def build_pdf(self, stock_symbol: str) -> tuple[bytes, str]:
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except ImportError as exc:
            raise ValueError("PDF reporting is unavailable until reportlab is installed.") from exc

        sentiment_result = SentimentAggregationService().analyze_stock(stock_symbol)
        if sentiment_result.get("error"):
            raise ValueError(sentiment_result["error"])

        buffer = io.BytesIO()
        document = SimpleDocTemplate(buffer, pagesize=A4, title=f"{sentiment_result['stock']} Sentiment Report")
        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"{sentiment_result['stock_name']} ({sentiment_result['stock']})", styles["Title"]),
            Spacer(1, 12),
            Paragraph(f"Overall sentiment: {sentiment_result['overall_sentiment']}", styles["Heading2"]),
            Paragraph(f"Average score: {sentiment_result['score']}", styles["BodyText"]),
            Spacer(1, 12),
        ]

        summary = sentiment_result["summary"]
        summary_table = Table(
            [
                ["Positive %", "Negative %", "Neutral %"],
                [f"{summary['positive']}%", f"{summary['negative']}%", f"{summary['neutral']}%"],
            ]
        )
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#114b5f")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d9cf")),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ]
            )
        )
        story.extend([summary_table, Spacer(1, 16), Paragraph("News Articles", styles["Heading2"]), Spacer(1, 8)])

        for index, article in enumerate(sentiment_result["articles"], start=1):
            story.append(Paragraph(f"{index}. {article['title']}", styles["Heading3"]))
            story.append(Paragraph(f"Published: {article['published_at'] or 'Unknown'}", styles["BodyText"]))
            story.append(Paragraph(f"Sentiment: {article['sentiment']['label']} ({article['sentiment']['score']})", styles["BodyText"]))
            if article.get("description"):
                story.append(Paragraph(article["description"], styles["BodyText"]))
            if article.get("url"):
                story.append(Paragraph(article["url"], styles["BodyText"]))
            story.append(Spacer(1, 10))

        document.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes, f"{sentiment_result['stock']}_sentiment_report.pdf"
