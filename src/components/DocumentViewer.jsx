import React, { useRef, useState } from "react";
import { Download, ArrowLeft } from "lucide-react";
import html2pdf from "html2pdf.js";

const DocumentationViewer = ({ data, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const contentRef = useRef(null);

  const generatePDF = async () => {
    if (!contentRef.current) return;
    try {
      setLoading(true);
      setError(null);

      const element = contentRef.current;
      const options = {
        margin: [10, 10],
        filename: "project-documentation.pdf",
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: {
          scale: 2,
          useCORS: true,
          letterRendering: true,
          backgroundColor: "#ffffff",
        },
        jsPDF: {
          unit: "mm",
          format: "a4",
          orientation: "portrait",
        },
      };

      await html2pdf().set(options).from(element).save();
    } catch (err) {
      setError("Failed to generate PDF. Please try again.");
      console.error("PDF generation error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!data) return null;

  const { architecture_analysis = {}, file_types_found = {} } = data;
  const totalFiles = Object.values(file_types_found).reduce((a, b) => a + b, 0);

  return (
    <div>
      {/* Header Navigation */}
      <div
        style={{
          padding: "12px 40px",
          backgroundColor: "white",
          borderBottom: "1px solid #eaeaea",
          position: "sticky",
          top: 0,
          zIndex: 100,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          maxWidth: "800px",
          margin: "0 auto",
        }}
      >
        <button
          onClick={onBack}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            border: "none",
            background: "none",
            cursor: "pointer",
            color: "#4b5563",
          }}
        >
          <ArrowLeft size={20} />
          Back to Input
        </button>

        <button
          onClick={generatePDF}
          disabled={loading}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            backgroundColor: loading ? "#93c5fd" : "#3b82f6",
            color: "white",
            border: "none",
            padding: "8px 16px",
            borderRadius: "6px",
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.7 : 1,
          }}
        >
          <Download size={20} />
          {loading ? "Generating PDF..." : "Download PDF"}
        </button>
      </div>

      {error && (
        <div
          style={{
            margin: "20px",
            padding: "12px",
            backgroundColor: "#fee2e2",
            color: "#b91c1c",
            borderRadius: "6px",
          }}
        >
          {error}
        </div>
      )}

      {/* Content to be converted to PDF */}
      <div
        ref={contentRef}
        style={{
          padding: "40px",
          maxWidth: "800px",
          margin: "0 auto",
          backgroundColor: "white",
        }}
      >
        <h1
          style={{
            fontSize: "32px",
            marginBottom: "32px",
            textAlign: "center",
            color: "#111827",
          }}
        >
          Project Documentation
        </h1>

        <section style={{ marginBottom: "40px" }}>
          <h2
            style={{
              fontSize: "24px",
              marginBottom: "16px",
              color: "#111827",
            }}
          >
            📊 Project File Composition
          </h2>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "8px",
              padding: "16px",
              backgroundColor: "#f9fafb",
              borderRadius: "8px",
            }}
          >
            {Object.entries(file_types_found).map(([type, count]) => (
              <span
                key={type}
                style={{
                  padding: "4px 12px",
                  backgroundColor: "#e6f2ff",
                  color: "#1e40af",
                  borderRadius: "16px",
                  fontSize: "14px",
                }}
              >
                {type}: {count} ({((count / totalFiles) * 100).toFixed(1)}%)
              </span>
            ))}
          </div>
        </section>

        {Object.entries(architecture_analysis).map(([section, content]) => (
          <section key={section} style={{ marginBottom: "40px" }}>
            <h2
              style={{
                fontSize: "24px",
                marginBottom: "16px",
                color: "#111827",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              {getIcon(section)} {section}
            </h2>
            <div
              style={{
                backgroundColor: "#f9fafb",
                padding: "16px",
                borderRadius: "8px",
                borderLeft: "4px solid #3b82f6",
              }}
            >
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  fontFamily: "inherit",
                  margin: 0,
                  color: "#374151",
                }}
              >
                {content}
              </pre>
            </div>
          </section>
        ))}
      </div>
    </div>
  );
};

const getIcon = (section) => {
  const icons = {
    "Project Architecture": "🏗️",
    "Project Overview": "📋",
    "Tech Stack": "💻",
    "Key Features in Components": "🧩",
    "Implementation Flow": "🔀",
    "Future Improvements": "🚀",
  };
  return icons[section] || "📝";
};

export default DocumentationViewer;
