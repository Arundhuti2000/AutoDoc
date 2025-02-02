// src/App.jsx
import { useState } from "react";
import axios from "axios";

function App() {
  const [sourcePath, setSourcePath] = useState("");
  const [destPath, setDestPath] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handlePathSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus("Processing files...");

    // Normalize paths by replacing backslashes with forward slashes
    const normalizedSourcePath = sourcePath.replace(/\\/g, "/");
    const normalizedDestPath = destPath.replace(/\\/g, "/");

    try {
      const response = await axios.post(
        "http://localhost:8000/analyze-folder",
        {
          source_path: normalizedSourcePath,
          destination_path: normalizedDestPath,
        }
      );

      if (response.data.pdf_path) {
        setStatus(
          "PDF generated successfully! Path: " + response.data.pdf_path
        );
      }
    } catch (error) {
      setStatus("Error: " + (error.response?.data?.detail || error.message));
      console.error("Full error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "20px" }}>Project Documentation Generator</h1>

      <div
        style={{
          marginBottom: "20px",
          padding: "20px",
          border: "1px solid #ccc",
          borderRadius: "4px",
        }}
      >
        <form onSubmit={handlePathSubmit}>
          {/* Source Path Input */}
          <div style={{ marginBottom: "15px" }}>
            <label
              htmlFor="sourcePath"
              style={{ display: "block", marginBottom: "5px" }}
            >
              Source Folder Path:
            </label>
            <input
              id="sourcePath"
              type="text"
              value={sourcePath}
              onChange={(e) => setSourcePath(e.target.value)}
              style={{
                width: "100%",
                padding: "8px",
                borderRadius: "4px",
                border: "1px solid #ccc",
              }}
              placeholder="D:/Personal Projects/Brown/project-architect"
            />
            <p style={{ marginTop: "5px", fontSize: "0.8em", color: "#666" }}>
              Example: D:/Personal Projects/Brown/project-architect
            </p>
          </div>

          {/* Destination Path Input */}
          <div style={{ marginBottom: "15px" }}>
            <label
              htmlFor="destPath"
              style={{ display: "block", marginBottom: "5px" }}
            >
              Destination Folder Path:
            </label>
            <input
              id="destPath"
              type="text"
              value={destPath}
              onChange={(e) => setDestPath(e.target.value)}
              style={{
                width: "100%",
                padding: "8px",
                borderRadius: "4px",
                border: "1px solid #ccc",
              }}
              placeholder="D:/Personal Projects/Brown/project-architect/docs"
            />
            <p style={{ marginTop: "5px", fontSize: "0.8em", color: "#666" }}>
              Example: D:/Personal Projects/Brown/project-architect/docs
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !sourcePath || !destPath}
            style={{
              padding: "10px 20px",
              backgroundColor:
                loading || !sourcePath || !destPath ? "#ccc" : "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor:
                loading || !sourcePath || !destPath ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Processing..." : "Generate Documentation"}
          </button>
        </form>
      </div>

      {status && (
        <div
          style={{
            padding: "15px",
            backgroundColor: status.includes("Error") ? "#ffe6e6" : "#e6ffe6",
            borderRadius: "4px",
            marginTop: "20px",
          }}
        >
          {status}
        </div>
      )}
    </div>
  );
}

export default App;
