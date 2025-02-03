from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import json
import requests
import pathlib
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import fpdf

class FolderRequest(BaseModel):
    source_path: str
    # destination_path: str

class DocumentationData(BaseModel):
    data: dict

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
    try:
        # Read the source code from the files in source_path
        source_code=""
        for pattern in ['**/*.py', '**/Dockerfile', '**/Makefile']:  # Add more patterns as needed
            for file_path in pathlib.Path(source_path).rglob(pattern):
                if file_path.is_file() and not any(excluded in str(file_path) for excluded in ['venv', '.venv', 'node_modules', '__pycache__', '.git']):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            source_code += f"\n# File: {file_path.name}\n"
                            source_code += f.read()
                    except Exception as e:
                        print(f"Error reading file {file_path}: {str(e)}")

            file_types_str = "File Types Distribution:\n" + "\n".join([
                    f"- {ftype}: {count} files" 
                    for ftype, count in file_types_found.items()
                ])
        prompt = f"""Provide a comprehensive architectural analysis for this project. Project File Composition: ```python

        Source Code:
        {source_code}
        {file_types_str}
        Analyze this project and provide a clear, detailed technical documentation with the following sections. For each section, provide detailed, specific information based on the actual code and files:
        1. Project Architecture:
            - How are the components organized?
            - What are the key architectural decisions?

        2. Project Overview:
            - What is the main purpose of this project?
            - What problem does it solve?
            - What are its core features?

        3. Tech Stack:
            - List all major technologies, frameworks, and libraries used
            - Explain why each technology was chosen
            - Describe version requirements if specified

        4. Key Features in Components:
            - Detail the main components and their responsibilities
            - Explain how components interact
            - Describe key functionality implemented in each major component

        5. Implementation Flow:
            - Explain the main workflow of the application
            - Describe how data flows between components
            - Detail key processes and their steps

        6. Future Improvements:
            - Suggest specific technical improvements
            - Identify potential optimizations
            - Recommend scalability enhancements

        Format each section clearly with detailed, specific information. Avoid generalities and focus on the actual implementation details found in the code.
        """
        
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

@app.post("/analyze-folder")
async def analyze_folder(request: FolderRequest):
    source_path = str(pathlib.Path(request.source_path).resolve())
    
    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail=f"Source folder not found: {source_path}")
    
    try:
        # Collect and categorize files
        file_types_found = analyze_files(source_path)
        
        # Generate architectural analysis
        architecture_analysis = analyze_architecture_with_ollama(source_path, file_types_found)
        
        return {
            "architecture_analysis": architecture_analysis,
            "file_types_found": file_types_found,
            "total_files": sum(file_types_found.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing folder: {str(e)}")



def get_section_icon(section: str) -> str:
    """Return the appropriate icon for each documentation section."""
    icons = {
        'Project Architecture': '🏗️',
        'Project Overview': '📋',
        'Tech Stack': '💻',
        'Key Features in Components': '🧩',
        'Implementation Flow': '🔀',
        'Future Improvements': '🚀',
    }
    return icons.get(section, '📝')

def analyze_files(source_path: str) -> dict:
    """Analyze and categorize files in the source directory."""
    file_types_found = {}
    
    try:
        # Collect all files recursively
        all_files = []
        for pattern in ['**/*.*', '**/Dockerfile', '**/Makefile']:
            found_files = list(pathlib.Path(source_path).rglob(pattern))
            all_files.extend([str(f) for f in found_files if f.is_file()])
        
        # Categorize files
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
            
        return file_types_found
        
    except Exception as e:
        print(f"Error analyzing files: {str(e)}")
        return {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)