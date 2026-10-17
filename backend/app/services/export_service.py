import csv
import io
from app.schemas.analysis import AnalysisResponse


class ExportService:
    """
    Generates sanitized, formula-safe CSV reports adhering to RFC 4180 standards.
    """

    FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

    @classmethod
    def sanitize_cell(cls, value: str) -> str:
        """
        Prevents CSV / Spreadsheet Formula Injection (CSV Injection / CWE-1236).
        Prepends a single quote if the string begins with risky spreadsheet operators.
        """
        if not isinstance(value, str):
            value = str(value)

        if value.startswith(cls.FORMULA_PREFIXES):
            return f"'{value}"
        return value

    @classmethod
    def generate_analysis_csv(cls, analysis: AnalysisResponse) -> str:
        """
        Generates a comprehensive, structured CSV document containing:
        1. Executive metadata and metrics
        2. Word frequency rankings
        3. Adjacent bigrams
        4. Word-length distributions
        """
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")

        # 1. Header / Metadata Section
        writer.writerow(["# WORD INTELLIGENCE ANALYSIS REPORT (v0.4)"])
        writer.writerow(["Source Type", cls.sanitize_cell(analysis.metadata.source_type)])
        writer.writerow(["Source Label", cls.sanitize_cell(analysis.metadata.source_name or "Raw Input")])
        writer.writerow(["Engine Used", cls.sanitize_cell(analysis.metadata.engine_used)])
        writer.writerow(["Execution Time (ms)", analysis.metadata.execution_time_ms or 0])
        writer.writerow(["Total Tokens", analysis.total_tokens])
        writer.writerow(["Unique Words", analysis.unique_tokens])
        writer.writerow(["Average Word Length", analysis.average_word_length])
        writer.writerow(["Raw Character Count", analysis.metadata.raw_character_count])

        if analysis.sentiment:
            writer.writerow(["Sentiment Label", cls.sanitize_cell(analysis.sentiment.label)])
            writer.writerow(["Sentiment Polarity", analysis.sentiment.polarity])
            writer.writerow(["Subjectivity Score", analysis.sentiment.subjectivity])

        writer.writerow([])  # Blank separator line

        # 2. Word Frequency Table
        writer.writerow(["# WORD FREQUENCY RANKING"])
        writer.writerow(["Rank", "Word", "Count", "Percentage (%)"])
        for idx, item in enumerate(analysis.word_frequencies, start=1):
            writer.writerow([
                idx,
                cls.sanitize_cell(item.word),
                item.count,
                item.percentage,
            ])

        writer.writerow([])  # Blank separator line

        # 3. Bigram Phrases Table
        if analysis.bigrams:
            writer.writerow(["# FREQUENT BIGRAMS (2-WORD PHRASES)"])
            writer.writerow(["Rank", "Bigram", "Count"])
            for idx, item in enumerate(analysis.bigrams, start=1):
                writer.writerow([
                    idx,
                    cls.sanitize_cell(item.bigram),
                    item.count,
                ])
            writer.writerow([])

        # 4. Word Length Distribution Table
        if analysis.word_length_distribution:
            writer.writerow(["# WORD LENGTH DISTRIBUTION"])
            writer.writerow(["Word Length (Characters)", "Frequency Count"])
            for item in analysis.word_length_distribution:
                writer.writerow([item.length, item.count])

        return output.getvalue()


export_service = ExportService()
