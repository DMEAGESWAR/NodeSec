import logging
from sqlalchemy.ext.asyncio import AsyncSession
from services.scan_service import GraphRepository
from jinja2 import Environment, FileSystemLoader
import pathlib

# WeasyPrint requires GTK/Pango native libs — not available on bare Windows.
# We do a lazy import inside generate_pdf() so the rest of the app still starts.
try:
    from weasyprint import HTML as WeasyHTML
    _WEASYPRINT_AVAILABLE = True
except Exception:
    WeasyHTML = None
    _WEASYPRINT_AVAILABLE = False

logger = logging.getLogger("nodesec.reports")

TEMPLATE_DIR = pathlib.Path(__file__).parent / "templates"


async def generate_pdf(scan, db: AsyncSession) -> bytes:
    """Generate a PDF report using WeasyPrint and Jinja2."""
    graph = await GraphRepository.get_graph_data(scan.id, db)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("report.html")

    score_class = "low"
    if scan.overall_score and scan.overall_score >= 75:
        score_class = "critical"
    elif scan.overall_score and scan.overall_score >= 50:
        score_class = "high"
    elif scan.overall_score and scan.overall_score >= 25:
        score_class = "medium"

    html = template.render(
        domain=getattr(scan.domain, "domain_name", "unknown"),
        scan_date=scan.started_at.strftime("%Y-%m-%d %H:%M UTC") if scan.started_at else "N/A",
        status=scan.status,
        overall_score=scan.overall_score or 0,
        score_class=score_class,
        chains=graph["chains"],
    )

    if _WEASYPRINT_AVAILABLE and WeasyHTML is not None:
        return WeasyHTML(string=html).write_pdf()
    else:
        logger.warning("WeasyPrint not available (missing GTK libs on Windows), returning HTML fallback")
        return html.encode("utf-8")