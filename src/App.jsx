import { useState } from "react";
import { Book } from "lucide-react";
import DocumentationViewer from "./components/DocumentViewer";

const styles = {
  container: {
    minHeight: "100vh",
    backgroundColor: "#f3f4f6",
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,Helvetica Neue, Arial, sans-serif',
  },
  header: {
    borderBottom: "1px solid #e5e7eb",
    backgroundColor: "white",
    padding: "16px",
  },
  headerContent: {
    maxWidth: "1200px",
    margin: "0 auto",
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },
  logo: {
    color: "#3b82f6",
    fontSize: "20px",
    fontWeight: "600",
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },
  main: {
    maxWidth: "1200px",
    margin: "0 auto",
    padding: "32px 16px",
  },
  formContainer: {
    maxWidth: "600px",
    width: "100%",
    margin: "0 auto",
    backgroundColor: "white",
    borderRadius: "8px",
    padding: "24px",
    boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
  },
  title: {
    fontSize: "24px",
    fontWeight: "600",
    color: "#111827",
    marginBottom: "8px",
  },
  subtitle: {
    color: "#6b7280",
    marginBottom: "24px",
  },
  formGroup: {
    marginBottom: "16px",
  },
  label: {
    display: "block",
    fontSize: "14px",
    fontWeight: "500",
    color: "#374151",
    marginBottom: "4px",
  },
  input: {
    width: "100%",
    padding: "8px 12px",
    borderRadius: "6px",
    border: "1px solid #d1d5db",
    fontSize: "14px",
    marginBottom: "4px",
    boxSizing: "border-box",
  },
  hint: {
    fontSize: "12px",
    color: "#6b7280",
  },
  button: {
    width: "100%",
    padding: "10px",
    backgroundColor: "#3b82f6",
    color: "white",
    border: "none",
    borderRadius: "6px",
    fontSize: "14px",
    fontWeight: "500",
    cursor: "pointer",
  },
  buttonDisabled: {
    backgroundColor: "#93c5fd",
    cursor: "not-allowed",
  },
  error: {
    backgroundColor: "#fee2e2",
    border: "1px solid #ef4444",
    borderRadius: "6px",
    padding: "12px",
    marginBottom: "16px",
    color: "#b91c1c",
  },
  footer: {
    textAlign: "center",
    padding: "16px",
    color: "#6b7280",
    fontSize: "14px",
  },
};

export default function App() {
  const [sourcePath, setSourcePath] = useState("");
  // const [destPath, setDestPath] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [documentationData, setDocumentationData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/analyze-folder", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          source_path: sourcePath.replace(/\\/g, "/"),
          // destination_path: destPath.replace(/\\/g, "/"),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to analyze folder");
      }

      const data = await response.json();
      setDocumentationData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // const handleDownloadPDF = async () => {
  //   try {
  //     const response = await fetch("http://localhost:8000/download-pdf", {
  //       method: "POST",
  //       headers: {
  //         "Content-Type": "application/json",
  //       },
  //       body: JSON.stringify({
  //         data: documentationData,
  //       }),
  //     });

  //     if (!response.ok) {
  //       throw new Error("Failed to generate PDF");
  //     }

  //     const blob = await response.blob();
  //     const url = window.URL.createObjectURL(blob);
  //     const a = document.createElement("a");
  //     a.href = url;
  //     a.download = "project-documentation.pdf";
  //     document.body.appendChild(a);
  //     a.click();
  //     document.body.removeChild(a);
  //     window.URL.revokeObjectURL(url);
  //   } catch (err) {
  //     setError("Error downloading PDF: " + err.message);
  //   }
  // };

  const handleDownloadPDF = async () => {
    setLoading(true);
    try {
      // Log the data being sent
      console.log("Sending data:", documentationData);

      const response = await fetch("http://localhost:8000/download-pdf", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          data: documentationData,
        }),
      });

      console.log("Response status:", response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Server error response:", errorText);
        throw new Error("Server error: " + response.status);
      }

      const blob = await response.blob();
      console.log("Received blob size:", blob.size);

      if (blob.size === 0) {
        throw new Error("Received empty PDF file");
      }

      // Create and trigger download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "project_documentation.pdf";
      document.body.appendChild(a);
      a.click();

      // Cleanup
      setTimeout(() => {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }, 100);
    } catch (error) {
      console.error("Download error:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setDocumentationData(null);
    setError(null);
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.headerContent}>
          <Book size={24} color="#3b82f6" />
          <span style={styles.logo}>AutoDoc</span>
        </div>
      </div>

      <main style={styles.main}>
        {error && <div style={styles.error}>{error}</div>}

        {!documentationData ? (
          <div style={styles.formContainer}>
            <h1 style={styles.title}>Documentation Generator</h1>
            <p style={styles.subtitle}>
              Enter the paths for your project documentation
            </p>

            <form onSubmit={handleSubmit}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Source Path</label>
                <input
                  type="text"
                  value={sourcePath}
                  onChange={(e) => setSourcePath(e.target.value)}
                  style={styles.input}
                  placeholder="D:\Projects\MyProject"
                />
                <p style={styles.hint}>Path to your project directory</p>
              </div>

              {/* <div style={styles.formGroup}>
                <label style={styles.label}>Destination Path</label>
                <input
                  type="text"
                  value={destPath}
                  onChange={(e) => setDestPath(e.target.value)}
                  style={styles.input}
                  placeholder="D:\Projects\MyProject\docs"
                />
                <p style={styles.hint}>
                  Where to save the generated documentation
                </p>
              </div> */}

              <button
                type="submit"
                disabled={loading || !sourcePath}
                style={{
                  ...styles.button,
                  ...(loading || !sourcePath ? styles.buttonDisabled : {}),
                }}
              >
                {loading
                  ? "Generating Documentation..."
                  : "Generate Documentation"}
              </button>
            </form>
          </div>
        ) : (
          <DocumentationViewer
            data={documentationData}
            onDownload={handleDownloadPDF}
            onBack={handleBack}
          />
        )}
      </main>

      <footer style={styles.footer}>
        Documentation Generator - Built with React and FastAPI
      </footer>
    </div>
  );
}
