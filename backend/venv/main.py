from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import requests
from typing import List, Dict
import pathlib

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

def get_file_type(file_path: str) -> str:
    """Determine the type of file based on its extension."""
    path = pathlib.Path(file_path)
    ext = path.suffix.lower()
    name = path.name

    for type_name, extensions in FILE_TYPES.items():
        if ext in extensions or name in extensions:
            return type_name
    return "other"

def should_process_file(file_path: str) -> bool:
    """Determine if a file should be processed."""
    path = pathlib.Path(file_path)
    
    # Check excluded directories
    for parent in path.parents:
        if parent.name in EXCLUDED_DIRS:
            return False
    
    # Check excluded files
    if path.name in EXCLUDED_FILES:
        return False
        
    # Check if it's a supported file type
    return path.suffix.lower() in SUPPORTED_EXTENSIONS or path.name in sum(FILE_TYPES.values(), [])

def analyze_with_ollama(file_path: str, content: str, file_type: str) -> str:
    """Send content to Ollama with context about the file type."""
    prompt = f"""Analyze this {file_type} code file and provide comprehensive documentation including:
    1. File Overview: Brief description of the file's purpose
    2. Key Components: Main classes, functions, or structures
    3. Dependencies: External libraries or modules used
    4. Implementation Details: Important algorithms or patterns
    5. Usage Examples: If applicable
    
    File: {file_path}
    Content:
    {content}
    """
    
    try:
        response = requests.post('http://localhost:11434/api/generate', 
            json={
                "model": "codellama",
                "prompt": prompt,
                "stream": False
            })
        
        result = response.json()
        return result.get('response', 'No analysis generated')
    except Exception as e:
        print(f"Error with Ollama: {str(e)}")
        return f"Error analyzing code: {str(e)}"

def generate_html_report(source_path: str, dest_path: str, documentation: List[tuple], file_types_found: Dict[str, int]) -> str:
    """Generate an HTML report with CSS styling."""
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Documentation</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            h1 {{
                text-align: center;
                color: #333;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
            }}
            .overview {{
                background-color: white;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            .file-section {{
                background-color: white;
                margin-bottom: 15px;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .file-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
                margin-bottom: 10px;
            }}
            .file-type {{
                color: #666;
                font-style: italic;
            }}
            pre {{
                background-color: #f8f8f8;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <h1>Project Documentation</h1>
        
        <div class="overview">
            <h2>Project Overview</h2>
            <h3>File Types Found:</h3>
            <ul>
                {"".join(f'<li>{ftype}: {count} files</li>' for ftype, count in file_types_found.items())}
            </ul>
            <p>Source Path: {source_path}</p>
        </div>
        
        {"".join(f'''
        <div class="file-section">
            <div class="file-header">
                <h2>File: {filename}</h2>
                <span class="file-type">({file_type})</span>
            </div>
            <pre>{analysis}</pre>
        </div>
        ''' for filename, file_type, analysis in documentation)}
    </body>
    </html>
    """
    
    # Write HTML file
    output_path = os.path.join(dest_path, "project_documentation.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return output_path

def generate_readme(source_path: str, dest_path: str, file_types_found: Dict[str, int], total_files: int, analyzed_files: int) -> str:
    """Generate a comprehensive README.md file."""
    readme_content = f"""# Project Documentation

## Project Overview

This documentation was generated automatically to provide insights into the project structure and components.

### Project Statistics
- **Total Files**: {total_files}
- **Analyzed Files**: {analyzed_files}

### File Type Breakdown
{"".join(f'- **{ftype}**: {count} files\n' for ftype, count in file_types_found.items())}

### Source Path
`{source_path}`

## Analysis Notes
- This documentation was generated using an automated script
- AI-assisted code analysis was performed using Ollama
- Detailed file-by-file documentation is available in the HTML report

## Excluded Directories
The following directories were automatically excluded from analysis:
{", ".join(sorted(EXCLUDED_DIRS))}

## Recommendations
1. Review the generated documentation thoroughly
2. Supplement with manual notes and explanations
3. Keep this documentation updated with project changes
"""
    
    # Write README file
    readme_path = os.path.join(dest_path, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    return readme_path

@app.post("/analyze-folder")
async def analyze_folder(request: FolderRequest):
    source_path = normalize_path(request.source_path)
    dest_path = normalize_path(request.destination_path)
    
    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail=f"Source folder not found: {source_path}")
    
    os.makedirs(dest_path, exist_ok=True)
    
    try:
        # Collect all files recursively
        all_files = []
        for pattern in ['**/*.*', '**/Dockerfile', '**/Makefile']:
            found_files = list(pathlib.Path(source_path).rglob(pattern))
            all_files.extend([str(f) for f in found_files if f.is_file()])
        
        # Filter and analyze files
        documentation = []
        file_types_found = {}
        
        for file_path in all_files:
            if should_process_file(file_path):
                try:
                    file_type = get_file_type(file_path)
                    file_types_found[file_type] = file_types_found.get(file_type, 0) + 1
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    relative_path = os.path.relpath(file_path, source_path)
                    analysis = analyze_with_ollama(relative_path, content, file_type)
                    documentation.append((relative_path, file_type, analysis))
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                    continue
        
        # Generate HTML Report
        html_path = generate_html_report(source_path, dest_path, documentation, file_types_found)
        
        # Generate README
        readme_path = generate_readme(
            source_path, 
            dest_path, 
            file_types_found, 
            len(all_files), 
            len(documentation)
        )
        
        return {
            "html_report_path": html_path,
            "readme_path": readme_path,
            "files_analyzed": len(documentation),
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