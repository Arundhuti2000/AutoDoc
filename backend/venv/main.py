from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import requests
import pathlib
import re

class FolderRequest(BaseModel):
    source_path: str
    destination_path: str

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Comprehensive mapping of file types to their categories
FILE_TYPES = {
    'python': ['.py', '.pyi', '.pyx', '.pyw'],
    'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
    'typescript': ['.ts', '.tsx'],
    'web': ['.html', '.htm', '.css', '.scss', '.sass', '.less', '.svg', '.vue', '.svelte'],
    'java': ['.java', '.jar', '.class', '.jsp'],
    'c_cpp': ['.c', '.cpp', '.h', '.hpp', '.cc'],
    'c_sharp': ['.cs', '.cshtml', '.csx'],
    'ruby': ['.rb', '.erb', '.gemspec', '.rake'],
    'php': ['.php', '.phtml', '.php4', '.php5'],
    'swift': ['.swift'],
    'go': ['.go'],
    'rust': ['.rs', '.rlib'],
    'kotlin': ['.kt', '.kts'],
    'scala': ['.scala'],
    'config': [
        '.json', '.yaml', '.yml', '.toml', '.ini', '.conf',
        '.config', '.xml', '.xsd', '.wsdl', '.properties'
    ],
    'docker': ['Dockerfile', '.dockerignore', 'docker-compose.yml'],
    'database': ['.sql', '.prisma', '.graphql', '.gql'],
    'documentation': ['.md', '.rst', '.txt', '.docx'],
    'shell': ['.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd', '.ps1'],
    'build': [
        'package.json', 'requirements.txt', 'setup.py',
        'pom.xml', 'build.gradle', 'build.sbt',
        'Makefile', 'CMakeLists.txt'
    ]
}

def analyze_architecture_with_ollama(source_path: str, file_types_found: dict) -> dict:
    """Generate a comprehensive architectural overview using Ollama."""
    # Prepare file types string for context
    file_types_str = "\n".join([f"- {ftype}: {count} files" for ftype, count in file_types_found.items()])
    
    prompt = f"""Provide a comprehensive architectural analysis for this project. 
    Project File Composition:
    {file_types_str}

    Analyze and provide details for the following sections:

    1. Project Architecture
    - Identify the overall architectural pattern
    - Describe the system's structural approach

    2. Project Overview
    - Summarize the project's primary purpose
    - Highlight the main objectives

    3. Tech Stack
    - List all primary technologies used
    - Explain the rationale behind technology choices

    4. Key Features in Components
    - Break down main system components
    - Describe the role and responsibility of each component

    5. Implementation Flow
    - Describe the high-level workflow
    - Explain how different components interact

    6. Future Improvements
    - Suggest potential enhancements
    - Identify areas for optimization or scaling

    Provide a structured, clear, and insightful analysis that gives a complete picture of the project's architecture and potential."""
    
    try:
        response = requests.post('http://localhost:11434/api/generate', 
            json={
                "model": "codellama",
                "prompt": prompt,
                "stream": False
            })
        
        result = response.json()
        analysis_text = result.get('response', 'No architectural analysis generated')
        
        # Parse the analysis into sections
        sections = {}
        current_section = None
        for line in analysis_text.split('\n'):
            # Check for section headers
            section_match = re.match(r'^(\d+\.\s*([^:]+)):', line)
            if section_match:
                current_section = section_match.group(2).strip()
                sections[current_section] = []
            elif current_section and line.strip():
                sections[current_section].append(line.strip())
        
        # Convert sections to dictionary with newline-joined text
        formatted_sections = {
            key: '\n'.join(value) for key, value in sections.items()
        }
        
        return formatted_sections
    
    except Exception as e:
        print(f"Error with Ollama: {str(e)}")
        return {
            "Project Architecture": f"Error generating architectural overview: {str(e)}",
            "Project Overview": "Unable to generate overview",
            "Tech Stack": "Unable to determine tech stack",
            "Key Features in Components": "No components analysis available",
            "Implementation Flow": "No implementation flow details",
            "Future Improvements": "No improvement suggestions generated"
        }

def generate_html_report(source_path: str, dest_path: str, architecture_analysis: dict, file_types_found: dict) -> str:
    """Generate an HTML report with comprehensive architectural overview."""
    # Calculate total files
    total_files = sum(file_types_found.values())
    
    # Create pie chart data for file types
    pie_chart_data = ", ".join([f"['{ftype}', {count}]" for ftype, count in file_types_found.items()])
    
    # Prepare sections HTML
    sections_html = ""
    section_order = [
        "Project Architecture", 
        "Project Overview", 
        "Tech Stack", 
        "Key Features in Components", 
        "Implementation Flow", 
        "Future Improvements"
    ]
    section_icons = {
        "Project Architecture": "🏗️",
        "Project Overview": "📋",
        "Tech Stack": "💻",
        "Key Features in Components": "🧩",
        "Implementation Flow": "🔀",
        "Future Improvements": "🚀"
    }
    
    for section in section_order:
        if section in architecture_analysis:
            sections_html += f"""
            <div class="card">
                <h2>{section_icons.get(section, '📝')} {section}</h2>
                <div class="section-content">
                    <pre>{architecture_analysis.get(section, 'No details available')}</pre>
                </div>
            </div>
            """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Comprehensive Architectural Overview</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
        <style>
            :root {{
                --primary-color: #3498db;
                --secondary-color: #2ecc71;
                --background-light: #f4f6f7;
                --text-dark: #2c3e50;
                --card-bg: #ffffff;
                --border-radius: 12px;
            }}
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Inter', sans-serif;
                line-height: 1.6;
                background-color: var(--background-light);
                color: var(--text-dark);
            }}
            .page {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                padding: 30px 0;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                border-radius: var(--border-radius);
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                font-weight: 600;
                letter-spacing: -1px;
                font-size: 2.5em;
            }}
            .card {{
                background: var(--card-bg);
                border-radius: var(--border-radius);
                box-shadow: 0 10px 25px rgba(0,0,0,0.08);
                padding: 25px;
                margin-bottom: 25px;
                transition: all 0.3s ease;
            }}
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            }}
            .card h2 {{
                border-bottom: 3px solid var(--primary-color);
                padding-bottom: 10px;
                margin-bottom: 15px;
                color: var(--primary-color);
            }}
            .section-content {{
                background-color: #f8f9fa;
                border-left: 4px solid var(--primary-color);
                padding: 15px;
                border-radius: 5px;
            }}
            .section-content pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
                font-family: 'Inter', monospace;
            }}
            .file-composition {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: center;
                margin-top: 15px;
            }}
            .file-type-tag {{
                background-color: var(--primary-color);
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.9em;
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            #file_type_chart {{
                width: 100%;
                height: 400px;
            }}
            @media (max-width: 768px) {{
                .page {{
                    padding: 10px;
                }}
                .header h1 {{
                    font-size: 1.8em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="page">
            <div class="header">
                <h1>🔍 Comprehensive Architectural Overview</h1>
            </div>

            <div class="card">
                <h2>📊 Project File Composition</h2>
                <div class="file-composition">
                    {"".join(f'<span class="file-type-tag"><strong>{ftype}</strong>: {count} ({count/total_files*100:.1f}%)</span>' for ftype, count in file_types_found.items())}
                </div>
                <div id="file_type_chart"></div>
            </div>

            {sections_html}
        </div>

        <script type="text/javascript">
            google.charts.load('current', {{'packages':['corechart']}});
            google.charts.setOnLoadCallback(drawChart);

            function drawChart() {{
                var data = google.visualization.arrayToDataTable([
                    ['File Type', 'Count'],
                    {pie_chart_data}
                ]);

                var options = {{
                    title: 'Project File Type Distribution',
                    backgroundColor: 'transparent',
                    chartArea: {{width: '80%', height: '70%'}},
                    legend: {{position: 'right'}},
                    colors: ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
                }};

                var chart = new google.visualization.PieChart(document.getElementById('file_type_chart'));
                chart.draw(data, options);
            }}
        </script>
    </body>
    </html>
    """
    
    # Write HTML file
    output_path = os.path.join(dest_path, "project_architecture.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return output_path

def generate_readme(source_path: str, dest_path: str, architecture_analysis: dict, file_types_found: dict) -> str:
    """Generate a comprehensive README with architectural insights."""
    # Prepare file type distribution
    file_types_str = "\n".join([f"- **{ftype}**: {count} files ({count/sum(file_types_found.values())*100:.1f}%)" for ftype, count in file_types_found.items()])
    
    # Construct README content
    readme_content = f"""# 🏗️ Project Architectural Overview

## Project Composition

### File Type Distribution
{file_types_str}

### Source Path
`{source_path}`

## 📋 Project Overview
{architecture_analysis.get('Project Overview', 'No overview available')}

## 💻 Tech Stack
{architecture_analysis.get('Tech Stack', 'No tech stack details available')}

## 🏗️ Project Architecture
{architecture_analysis.get('Project Architecture', 'No architectural details available')}

## 🧩 Key Components
{architecture_analysis.get('Key Features in Components', 'No component details available')}

## 🔀 Implementation Flow
{architecture_analysis.get('Implementation Flow', 'No implementation flow details available')}

## 🚀 Future Improvements
{architecture_analysis.get('Future Improvements', 'No improvement suggestions available')}

---

*Automatically generated architectural overview*
"""
    
    # Write README file
    readme_path = os.path.join(dest_path, "ARCHITECTURE.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    return readme_path

@app.post("/analyze-folder")
async def analyze_folder(request: FolderRequest):
    source_path = str(pathlib.Path(request.source_path).resolve())
    dest_path = str(pathlib.Path(request.destination_path).resolve())
    
    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail=f"Source folder not found: {source_path}")
    
    os.makedirs(dest_path, exist_ok=True)
    
    try:
        # Collect all files recursively
        all_files = []
        for pattern in ['**/*.*', '**/Dockerfile', '**/Makefile']:
            found_files = list(pathlib.Path(source_path).rglob(pattern))
            all_files.extend([str(f) for f in found_files if f.is_file()])
        
        # Categorize files
        file_types_found = {}
        for file_path in all_files:
            if any(excluded in file_path for excluded in ['venv', '.venv', 'node_modules', '__pycache__', '.git']):
                continue
            
            file_ext = pathlib.Path(file_path).suffix.lower()
            file_type = 'other'
            for type_name, extensions in FILE_TYPES.items():
                if file_ext in extensions or pathlib.Path(file_path).name in extensions:
                    file_type = type_name
                    break
            
            file_types_found[file_type] = file_types_found.get(file_type, 0) + 1
        
        # Generate Architectural Overview
        architecture_analysis = analyze_architecture_with_ollama(source_path, file_types_found)
        
        # Generate HTML Report
        html_path = generate_html_report(
            source_path, 
            dest_path, 
            architecture_analysis, 
            file_types_found
        )
        
        # Generate README
        readme_path = generate_readme(
            source_path, 
            dest_path, 
            architecture_analysis, 
            file_types_found
        )
        
        return {
            "html_report_path": html_path,
            "readme_path": readme_path,
            "total_files_found": len(all_files),
            "file_types": file_types_found
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing folder: {str(e)}")

def normalize_path(path: str) -> str:
    return str(pathlib.Path(path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)