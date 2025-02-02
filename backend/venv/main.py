from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import requests
import pathlib
from collections import Counter

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
    'docker': ['Dockerfile', '.dockerignage', 'docker-compose.yml'],
    'database': ['.sql', '.prisma', '.graphql', '.gql'],
    'documentation': ['.md', '.rst', '.txt', '.docx'],
    'shell': ['.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd', '.ps1'],
    'build': [
        'package.json', 'requirements.txt', 'setup.py',
        'pom.xml', 'build.gradle', 'build.sbt',
        'Makefile', 'CMakeLists.txt'
    ]
}

# Flatten the list of supported extensions
SUPPORTED_EXTENSIONS = {
    ext for extensions in FILE_TYPES.values() 
    for ext in extensions
}

# Common exclude patterns
EXCLUDED_DIRS = {
    'venv', '.venv', 'node_modules', '__pycache__', '.git',
    '.idea', '.vscode', 'build', 'dist', 'env', 'migrations',
    'tmp', 'temp', 'cache', '.next', '.nuxt', 'coverage',
    'bin', 'obj', 'target', '.terraform'
}

EXCLUDED_FILES = {
    '.pyc', '.pyo', '.pyd', '.db', '.sqlite3', '.log',
    '.env', '.env.local', '.DS_Store', 'package-lock.json',
    'yarn.lock', '.gitignore', '.dockerignore', 'Thumbs.db',
    '*.min.js', '*.min.css'
}

def analyze_architecture_with_ollama(source_path: str, file_types_found: dict) -> str:
    """Generate a high-level architectural overview using Ollama."""
    prompt = f"""Provide a comprehensive high-level architectural overview of the project based on the following file type composition:

File Types Composition:
{json.dumps(file_types_found, indent=2)}

Project Root: {source_path}

Please analyze and describe:
1. Probable Architectural Pattern (Microservices, Monolith, Layered, etc.)
2. Key Technology Stack
3. Potential System Components
4. Estimated Scalability and Performance Characteristics
5. Architectural Strengths and Potential Improvement Areas

Provide a concise yet informative summary that captures the essence of the project's architecture."""
    
    try:
        response = requests.post('http://localhost:11434/api/generate', 
            json={
                "model": "codellama",
                "prompt": prompt,
                "stream": False
            })
        
        result = response.json()
        return result.get('response', 'No architectural analysis generated')
    except Exception as e:
        print(f"Error with Ollama: {str(e)}")
        return f"Error generating architectural overview: {str(e)}"

def generate_html_report(source_path: str, dest_path: str, architecture_overview: str, file_types_found: dict) -> str:
    """Generate an HTML report with high-level architectural overview."""
    # Calculate total files
    total_files = sum(file_types_found.values())
    
    # Create pie chart data for file types
    pie_chart_data = ", ".join([f"['{ftype}', {count}]" for ftype, count in file_types_found.items()])
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Architectural Overview</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
        <style>
            :root {{
                --primary-color: #3498db;
                --secondary-color: #2ecc71;
                --background-light: #f4f6f7;
                --text-dark: #2c3e50;
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
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
            }}
            .header {{
                grid-column: 1 / -1;
                text-align: center;
                padding: 20px 0;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            .header h1 {{
                font-weight: 600;
                letter-spacing: -1px;
            }}
            .card {{
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                padding: 25px;
                transition: transform 0.3s ease;
            }}
            .card:hover {{
                transform: translateY(-5px);
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
            .architectural-overview {{
                white-space: pre-wrap;
                font-family: 'Inter', monospace;
                background-color: #f8f9fa;
                border-left: 4px solid var(--primary-color);
                padding: 15px;
                border-radius: 5px;
            }}
            #file_type_chart {{
                width: 100%;
                height: 400px;
            }}
            @media (max-width: 768px) {{
                .page {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="page">
            <div class="header">
                <h1>📊 Project Architectural Overview</h1>
            </div>

            <div class="card">
                <h2>🗂️ Project File Composition</h2>
                <div class="file-composition">
                    {"".join(f'<span class="file-type-tag"><strong>{ftype}</strong>: {count} ({count/total_files*100:.1f}%)</span>' for ftype, count in file_types_found.items())}
                </div>
                <div id="file_type_chart"></div>
            </div>

            <div class="card">
                <h2>🏗️ Architectural Analysis</h2>
                <div class="architectural-overview">{architecture_overview}</div>
            </div>
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

def generate_readme(source_path: str, dest_path: str, architecture_overview: str, file_types_found: dict) -> str:
    """Generate a comprehensive README with architectural insights."""
    readme_content = f"""# Project Architectural Overview

## Project Composition

### File Type Distribution
{"".join(f'- **{ftype}**: {count} files\n' for ftype, count in file_types_found.items())}

### Source Path
`{source_path}`

## Architectural Analysis

{architecture_overview}

## Key Insights
- Automatically generated architectural overview
- Provides high-level system perspective
- Identifies potential architectural patterns and technologies

## Recommendations
1. Review the architectural overview carefully
2. Validate assumptions with project stakeholders
3. Use as a starting point for architectural discussions
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
            if any(excluded in file_path for excluded in EXCLUDED_DIRS):
                continue
            
            file_ext = pathlib.Path(file_path).suffix.lower()
            file_type = 'other'
            for type_name, extensions in FILE_TYPES.items():
                if file_ext in extensions:
                    file_type = type_name
                    break
            
            file_types_found[file_type] = file_types_found.get(file_type, 0) + 1
        
        # Generate Architectural Overview
        architecture_overview = analyze_architecture_with_ollama(source_path, file_types_found)
        
        # Generate HTML Report
        html_path = generate_html_report(
            source_path, 
            dest_path, 
            architecture_overview, 
            file_types_found
        )
        
        # Generate README
        readme_path = generate_readme(
            source_path, 
            dest_path, 
            architecture_overview, 
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)