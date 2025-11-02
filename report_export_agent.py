from reportlab.pdfgen import canvas

def export_report(summary, charts, filename="AI_Agent_Report.pdf"):
    """Generate a PDF report combining stats and visuals."""
    print("\n📝 Generating Report...")

    c = canvas.Canvas(filename)
    c.setFont("Helvetica", 14)
    c.drawString(100, 800, "AI Agent Data Analysis Report")

    y = 770
    for col in summary.columns[:5]:
        mean_value = summary[col].get('mean', 'N/A')
        # ✅ Only round numbers
        if isinstance(mean_value, (int, float)):
            mean_value = round(mean_value, 2)
        else:
            mean_value = str(mean_value)
        c.setFont("Helvetica", 10)
        c.drawString(100, y, f"{col}: mean = {mean_value}")
        y -= 15

    # Add charts
    for chart in charts:
        y -= 180
        if y < 100:  # Move to new page if space runs out
            c.showPage()
            y = 770
        c.drawImage(chart, 100, y, width=400, height=200)

    c.save()
    print(f"✅ Report exported successfully as {filename}")
