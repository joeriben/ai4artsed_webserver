#!/usr/bin/env python3
"""
Script to generate/update the exports.html overview page
"""
import json
from pathlib import Path
from datetime import datetime

def generate_exports_html():
    """Generate exports.html overview page"""
    exports_dir = Path("../exports")
    html_dir = exports_dir / "html"
    pdf_dir = exports_dir / "pdf"
    xml_dir = exports_dir / "xml"
    docx_dir = exports_dir / "docx"
    
    sessions = []
    
    # Scan html directory for sessions
    if html_dir.exists():
        for session_dir in html_dir.iterdir():
            if session_dir.is_dir() and session_dir.name.startswith('session_'):
                metadata_path = session_dir / 'metadata.json'
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # Extract session info
                        user_id = metadata.get('user_id', 'N/A')
                        session_id = metadata.get('session_id', 'N/A')
                        timestamp = metadata.get('timestamp', 'N/A')
                        workflow_name = metadata.get('workflow_name', 'N/A')
                        workflow_clean = workflow_name.replace('.json', '') if workflow_name != 'N/A' else 'unknown'
                        prompt = metadata.get('prompt', '')
                        export_date = metadata.get('export_date', '')
                        
                        # Look for HTML file
                        html_files = list(session_dir.glob(f"output_{user_id}_{timestamp}_{session_id}_*.html"))
                        if html_files:
                            html_file = html_files[0].name
                        else:
                            html_file = f"output_{user_id}_{timestamp}_{session_id}.html"
                        
                        # Check for other export files
                        pdf_file = pdf_dir / f"output_{user_id}_{timestamp}_{session_id}_{workflow_clean}.pdf"
                        xml_file = xml_dir / f"export_{user_id}_{timestamp}_{session_id}_{workflow_clean}.xml"
                        docx_file = docx_dir / f"export_{user_id}_{timestamp}_{session_id}_{workflow_clean}.docx"
                        
                        sessions.append({
                            'folder_name': session_dir.name,
                            'html_file': html_file,
                            'user_id': user_id,
                            'session_id': session_id,
                            'timestamp': timestamp,
                            'workflow_name': workflow_name,
                            'workflow_clean': workflow_clean,
                            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
                            'export_date': export_date,
                            'has_pdf': pdf_file.exists(),
                            'has_xml': xml_file.exists(),
                            'has_docx': docx_file.exists(),
                            'pdf_file': pdf_file.name if pdf_file.exists() else None,
                            'xml_file': xml_file.name if xml_file.exists() else None,
                            'docx_file': docx_file.name if docx_file.exists() else None
                        })
                    except Exception as e:
                        print(f"Error reading metadata for {session_dir.name}: {e}")
    
    # Sort sessions by timestamp (newest first)
    sessions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI4ArtsEd Export Übersicht</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f0f2f5;
            color: #1c1e21;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            padding: 24px;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 12px;
            margin-bottom: 24px;
        }}
        .stats {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 24px;
            display: flex;
            gap: 30px;
        }}
        .stat-item {{
            flex: 1;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .session {{
            background-color: #f8f9fa;
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}
        .session:hover {{
            background-color: #e7f3ff;
            border-color: #007bff;
        }}
        .session-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .session-info {{
            flex: 1;
        }}
        .session-title {{
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }}
        .session-meta {{
            color: #666;
            font-size: 0.9em;
            margin-top: 4px;
        }}
        .session-prompt {{
            color: #555;
            font-style: italic;
            margin-top: 8px;
            padding: 8px;
            background: white;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .session-links {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }}
        .session-link {{
            padding: 6px 12px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.85em;
            transition: background-color 0.3s ease;
        }}
        .session-link:hover {{
            background-color: #0056b3;
        }}
        .session-link.secondary {{
            background-color: #6c757d;
        }}
        .session-link.secondary:hover {{
            background-color: #545b62;
        }}
        .session-link.disabled {{
            background-color: #e9ecef;
            color: #6c757d;
            cursor: not-allowed;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AI4ArtsEd Export Übersicht</h1>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{len(sessions)}</div>
                <div class="stat-label">Gesamt-Sessions</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{sum(1 for s in sessions if s['has_pdf'])}</div>
                <div class="stat-label">PDF Exports</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{sum(1 for s in sessions if s['has_docx'])}</div>
                <div class="stat-label">DOCX Exports</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{sum(1 for s in sessions if s['has_xml'])}</div>
                <div class="stat-label">XML Exports</div>
            </div>
        </div>
"""

    for session in sessions:
        # Format timestamp for display
        try:
            dt = datetime.strptime(session['timestamp'], '%y%m%d%H%M%S')
            display_date = dt.strftime('%d.%m.%Y %H:%M:%S')
        except:
            display_date = session['timestamp']
        
        html_content += f"""
        <div class="session">
            <div class="session-header">
                <div class="session-info">
                    <div class="session-title">{session['workflow_clean']}</div>
                    <div class="session-meta">
                        Session: {session['session_id']} | User: {session['user_id']} | {display_date}
                    </div>
                    <div class="session-prompt">{session['prompt']}</div>
                </div>
            </div>
            <div class="session-links">
                <a href="html/{session['folder_name']}/{session['html_file']}" class="session-link">HTML anzeigen</a>
"""
        
        if session['has_pdf']:
            html_content += f"""                <a href="pdf/{session['pdf_file']}" class="session-link secondary">PDF</a>
"""
        else:
            html_content += """                <span class="session-link disabled">PDF</span>
"""
            
        if session['has_docx']:
            html_content += f"""                <a href="docx/{session['docx_file']}" class="session-link secondary">DOCX</a>
"""
        else:
            html_content += """                <span class="session-link disabled">DOCX</span>
"""
            
        if session['has_xml']:
            html_content += f"""                <a href="xml/{session['xml_file']}" class="session-link secondary">XML</a>
"""
        else:
            html_content += """                <span class="session-link disabled">XML</span>
"""
        
        html_content += """            </div>
        </div>
"""

    html_content += f"""
        <div class="footer">
            <p>AI4ArtsEd - Artificial Intelligence for Arts Education</p>
            <p>Übersicht generiert: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}</p>
            <p>Anzahl Sessions: {len(sessions)}</p>
        </div>
    </div>
</body>
</html>"""

    # Write exports.html
    exports_html_path = exports_dir / "exports.html"
    with open(exports_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Successfully updated exports.html with {len(sessions)} sessions")
    print(f"PDF: {sum(1 for s in sessions if s['has_pdf'])}, DOCX: {sum(1 for s in sessions if s['has_docx'])}, XML: {sum(1 for s in sessions if s['has_xml'])}")

if __name__ == "__main__":
    generate_exports_html()
