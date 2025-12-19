"""
Report generation utilities for benchmark results.
M10: Generate detailed HTML/Markdown reports.
"""
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class ReportGenerator:
    """Generate formatted reports from benchmark results"""
    
    @staticmethod
    def generate_markdown(report: Dict[str, Any], output_path: str):
        """Generate Markdown report"""
        md_lines = []
        
        # Title
        md_lines.append("# NL2SQL Benchmark Report\n")
        md_lines.append(f"**Generated:** {report.get('timestamp', 'N/A')}\n")
        md_lines.append("---\n")
        
        # Summary
        summary = report.get('summary', {})
        md_lines.append("## 📊 Summary\n")
        md_lines.append(f"- **Total Cases:** {summary.get('total_cases', 0)}")
        md_lines.append(f"- **Total Time:** {summary.get('total_time', 0)}s")
        md_lines.append(f"- **Avg Time/Case:** {summary.get('avg_time_per_case', 0)}s\n")
        
        # Metrics
        metrics = summary.get('metrics', {})
        md_lines.append("## 📈 Metrics\n")
        md_lines.append("| Metric | Value |")
        md_lines.append("|--------|-------|")
        md_lines.append(f"| SQL Exact Match Rate | {metrics.get('sql_exact_match_rate', 0)}% |")
        md_lines.append(f"| SQL Semantic Match Rate | {metrics.get('sql_semantic_match_rate', 0)}% |")
        md_lines.append(f"| Execution Success Rate | {metrics.get('execution_success_rate', 0)}% |")
        md_lines.append(f"| Execution Accuracy Rate | {metrics.get('execution_accuracy_rate', 0)}% |\n")
        
        # By Category
        by_category = report.get('by_category', {})
        if by_category:
            md_lines.append("## 📂 Results by Category\n")
            md_lines.append("| Category | Total | Exact Match | Execution Success |")
            md_lines.append("|----------|-------|-------------|-------------------|")
            for cat, stats in sorted(by_category.items()):
                md_lines.append(
                    f"| {cat} | {stats['total']} | "
                    f"{stats['sql_exact_match_rate']}% | "
                    f"{stats['execution_success_rate']}% |"
                )
            md_lines.append("")
        
        # Failed Cases
        results = report.get('results', [])
        failed_cases = [r for r in results if not r.get('execution_success')]
        if failed_cases:
            md_lines.append("## ❌ Failed Cases\n")
            for i, case in enumerate(failed_cases, 1):
                md_lines.append(f"### {i}. {case.get('question')}")
                md_lines.append(f"- **Category:** {case.get('category')}")
                md_lines.append(f"- **Generated SQL:** `{case.get('generated_sql', 'N/A')}`")
                md_lines.append(f"- **Error:** {case.get('error', 'N/A')}\n")
        
        # Success Highlights
        success_cases = [r for r in results if r['metrics']['sql_exact_match']]
        if success_cases:
            md_lines.append("## ✅ Exact Match Examples\n")
            for i, case in enumerate(success_cases[:5], 1):
                md_lines.append(f"### {i}. {case.get('question')}")
                md_lines.append(f"```sql\n{case.get('generated_sql')}\n```\n")
        
        # Write to file
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write("\n".join(md_lines))
        
        print(f"✓ Markdown report saved to: {output}")
    
    @staticmethod
    def generate_html(report: Dict[str, Any], output_path: str):
        """Generate HTML report"""
        summary = report.get('summary', {})
        metrics = summary.get('metrics', {})
        by_category = report.get('by_category', {})
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NL2SQL Benchmark Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #4CAF50;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .success {{
            color: #4CAF50;
        }}
        .failure {{
            color: #f44336;
        }}
        .timestamp {{
            color: #999;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 NL2SQL Benchmark Report</h1>
        <p class="timestamp">Generated: {report.get('timestamp', 'N/A')}</p>
        
        <h2>Summary</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{summary.get('total_cases', 0)}</div>
                <div class="metric-label">Total Test Cases</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('sql_exact_match_rate', 0)}%</div>
                <div class="metric-label">SQL Exact Match Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('execution_success_rate', 0)}%</div>
                <div class="metric-label">Execution Success Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary.get('avg_time_per_case', 0)}s</div>
                <div class="metric-label">Avg Time per Case</div>
            </div>
        </div>
        
        <h2>Results by Category</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Total Cases</th>
                <th>Exact Match Rate</th>
                <th>Execution Success Rate</th>
            </tr>
"""
        
        for cat, stats in sorted(by_category.items()):
            html += f"""
            <tr>
                <td>{cat}</td>
                <td>{stats['total']}</td>
                <td>{stats['sql_exact_match_rate']}%</td>
                <td>{stats['execution_success_rate']}%</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>Detailed Results</h2>
        <p>See JSON report for complete details.</p>
    </div>
</body>
</html>
"""
        
        # Write to file
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ HTML report saved to: {output}")


if __name__ == "__main__":
    """Test report generation"""
    # Load a sample report
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <report.json>")
        sys.exit(1)
    
    report_path = sys.argv[1]
    
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Generate reports
        base_name = Path(report_path).stem
        
        md_path = f"eval/reports/{base_name}.md"
        html_path = f"eval/reports/{base_name}.html"
        
        generator = ReportGenerator()
        generator.generate_markdown(report, md_path)
        generator.generate_html(report, html_path)
        
        print("\n✓ Report generation complete")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
