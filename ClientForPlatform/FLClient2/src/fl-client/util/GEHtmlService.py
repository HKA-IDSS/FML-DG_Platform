import os
import datetime
import json

class GEHtmlService:
    def build_and_save_html(self, ge_data: dict) -> str:
        """Creates a HTML Report from a Great Expectations Validation Result and saves it to a file."""
        
        success_global = ge_data.get("success", False)
        suite_name = ge_data.get("suite_name", "N/A")
        suite_params = ge_data.get("suite_parameters", {})
        stats = ge_data.get("statistics", {})
        meta = ge_data.get("meta", {})
        results = ge_data.get("results", [])

        styles = """
<style>
  body { font-family: Arial, sans-serif; margin: 20px; }
  h1, h2, h3 { margin-bottom: 0.4em; }
  .section { margin-bottom: 1.5em; }
  ul { list-style-type: disc; margin-left: 20px; }
  .success-true { color: green; }
  .success-false { color: red; }
  summary { font-weight: bold; cursor: pointer; }
  details {
    margin-bottom: 1em; padding: 0.5em;
    border: 1px solid #ccc; border-radius: 4px;
    background-color: #fafafa;
  }
  table { border-collapse: collapse; margin: 0.5em 0; width: 100%; }
  table, th, td { border: 1px solid #ccc; }
  th, td { padding: 6px 8px; vertical-align: top; }
  th { background-color: #f2f2f2; text-align: left; }
  code { background-color: #eee; padding: 2px 4px; border-radius: 4px; }
  .exception-traceback {
    white-space: pre-wrap; font-family: monospace;
    background-color: #f9f9f9; padding: 8px;
    border: 1px solid #ddd; border-radius: 4px;
    margin: 0.5em 0;
  }
</style>
"""

        html_report = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>GE Validation Report</title>
  {styles}
</head>
<body>
  <h1>Great Expectations Validation Report</h1>
  <div class="section">
    <h2>Overview</h2>
    <p><strong>Overall success:</strong>
       <span class="success-{str(success_global).lower()}">{success_global}</span>
    </p>
    <p><strong>Suite name:</strong> {suite_name}</p>
  </div>
"""

        if suite_params:
            html_report += """
  <div class="section">
    <h2>Suite Parameters</h2>
    <ul>
"""
            for key, val in suite_params.items():
                html_report += f"      <li><strong>{key}</strong>: {val}</li>"
            html_report += "    </ul>\n  </div>\n"

        html_report += f"""
  <div class="section">
    <h2>Statistics</h2>
    <ul>
      <li>Evaluated expectations: {stats.get('evaluated_expectations', 'N/A')}</li>
      <li>Successful expectations: {stats.get('successful_expectations', 'N/A')}</li>
      <li>Unsuccessful expectations: {stats.get('unsuccessful_expectations', 'N/A')}</li>
      <li>Success percent: {stats.get('success_percent', 'N/A')}</li>
    </ul>
  </div>
"""

        if meta:
            html_report += """
  <div class="section">
    <h2>Meta</h2>
    <ul>
"""
            for key, val in meta.items():
                if isinstance(val, dict):
                    html_report += f"""      <li><strong>{key}:</strong><br>
        <code>{json.dumps(val, indent=2)}</code>
      </li>
"""
                else:
                    html_report += f"      <li><strong>{key}:</strong> {val}</li>"
            html_report += "    </ul>\n  </div>\n"

        html_report += """
  <div class="section">
    <h2>Detailed Expectations</h2>
"""
        for i, item in enumerate(results, start=1):
            success = item.get("success", False)
            config = item.get("expectation_config", {})
            result_obj = item.get("result", {})
            exception_info = item.get("exception_info", {})

            exp_type = config.get("type", "unknown")
            exp_id = config.get("id", "N/A")
            kwargs = config.get("kwargs", {})
            meta_ = config.get("meta", {})

            html_report += f"""
    <details>
      <summary>#{i} | Expectation: {exp_type} | Success:
        <span class="success-{str(success).lower()}">{success}</span>
      </summary>
      <div style="margin: 10px 0;">
        <table>
          <tr><th>Expectation Type</th><td>{exp_type}</td></tr>
          <tr><th>Expectation ID</th><td>{exp_id}</td></tr>
          <tr><th>Success</th>
            <td class="success-{str(success).lower()}">{success}</td></tr>
"""

            if kwargs:
                html_report += """
          <tr><th>Kwargs</th><td>
            <ul>
"""
                for k, v in kwargs.items():
                    html_report += f"              <li><strong>{k}</strong>: {v}</li>"
                html_report += "            </ul>\n          </td></tr>\n"

            if meta_:
                html_report += f"""
          <tr><th>Config Meta</th><td>
            <code>{json.dumps(meta_, indent=2)}</code>
          </td></tr>
"""

            if result_obj:
                html_report += """
          <tr><th>Result</th><td>
            <ul>
"""
                for rk, rv in result_obj.items():
                    if isinstance(rv, (dict, list)):
                        rv_str = json.dumps(rv, indent=2)
                        html_report += f"              <li><strong>{rk}</strong>: <pre>{rv_str}</pre></li>"
                    else:
                        html_report += f"              <li><strong>{rk}</strong>: {rv}</li>"
                html_report += "            </ul>\n          </td></tr>\n"

            if exception_info:
                html_report += """
          <tr><th>Exception Info</th><td>
"""
                for subkey, subval in exception_info.items():
                    if isinstance(subval, dict):
                        trace = subval.get("exception_traceback", "")
                        msg = subval.get("exception_message", "")
                        raised = subval.get("raised_exception", False)
                        html_report += f"""
            <details>
              <summary><strong>{subkey}</strong> | raised_exception={raised}</summary>
              <div style="margin: 10px 0;">
"""
                        if msg:
                            html_report += f"                <p><strong>Message:</strong> {msg}</p>"
                        if trace:
                            html_report += f"                <div class='exception-traceback'>{trace}</div>"
                        html_report += "              </div>\n            </details>\n"
                    else:
                        html_report += f"            <p><strong>{subkey}:</strong> {subval}</p>"
                html_report += "          </td></tr>\n"

            html_report += "        </table>\n      </div>\n    </details>\n"

        html_report += "  </div>\n</body>\n</html>\n"

        os.makedirs("src/fl-client/tmp", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"src/fl-client/tmp/{timestamp}_validation_report.html"
        with open(filename, "w+", encoding="utf-8") as f:
            f.write(html_report)
        return filename
