# AutoDoc - Project Documentation Generator

AutoDoc is a web application that automatically generates comprehensive documentation for your projects. It analyzes your project's structure, files, and code to create detailed technical documentation with insights about architecture, tech stack, and code organization.

## 🚀 Features

- **Automated Analysis**: Scans your project directory and analyzes code patterns
- **File Composition Analysis**: Provides detailed breakdown of file types in your project
- **Architecture Documentation**: Generates comprehensive insights about project structure
- **Tech Stack Analysis**: Identifies and documents technologies used
- **PDF Export**: Export documentation to PDF format
- **Clean UI**: Modern, responsive interface for viewing documentation

## 🛠️ Tech Stack

### Frontend
- React.js
- Lucide Icons
- html2pdf.js for PDF generation

### Backend
- FastAPI (Python)
- Ollama with CodeLlama model for code analysis

## 🔧 Installation

### Prerequisites
- Python 3.7+
- Node.js
- Ollama with CodeLlama model installed

### Backend Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/autodoc.git
cd autodoc
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies
```bash
pip install fastapi uvicorn python-multipart requests
```

4. Start the backend server
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup
1. Navigate to frontend directory
```bash
cd frontend
```

2. Install dependencies
```bash
npm install
```

3. Start the development server
```bash
npm run dev
```

## 💻 Usage

1. Open http://localhost:5173 in your browser
2. Enter the source path of the project you want to analyze
3. Enter the destination path for generated documentation
4. Click "Generate Documentation"
5. View the generated documentation and export to PDF if needed

## 🏗️ Project Structure

```
project/
├── backend/
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── DocumentationViewer.jsx
    │   └── App.jsx
    ├── package.json
    └── index.html
```

## ✨ Features in Detail

- **Project Overview**: Automatically generates a comprehensive overview of your project's purpose and main objectives
- **Architecture Analysis**: Identifies architectural patterns and structural approaches used in your project
- **Tech Stack Documentation**: Lists and explains all technologies used in your project
- **Component Analysis**: Breaks down main system components and their responsibilities
- **Implementation Flow**: Documents how different components interact
- **Future Improvements**: Suggests potential enhancements and optimizations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
## 📞 Support
For support, please:

Open an issue on GitHub
Check existing issues for solutions
Review documentation for common fixes

Home:
![home](https://github.com/user-attachments/assets/ac097058-93d8-42b0-8152-0816798e60b7)
Document Genrated:
![DocumentGenerated4](https://github.com/user-attachments/assets/5ed58833-b0d5-4902-ad67-997f1af2acab)

Sample PDF:
![image](https://github.com/user-attachments/assets/41bc51a8-5007-487c-ad7f-753bf2c5bc62)


