# Textricator: Finite State Machine Document Extraction

## 1. Synthesis

**Repository:** `measuresforjustice/textricator`
**Language:** Kotlin
**Core Purpose:** A deterministic, configuration-driven tool for extracting structured data from PDFs and other document formats using Finite State Machines (FSMs) and spatial analysis.

### Key Capabilities
*   **Spatial Text Extraction:** Extracts text with precise coordinate (x, y), font, and style metadata using PDFBox or iText.
*   **FSM Parsing Engine:** Uses a YAML-configurable Finite State Machine to traverse the stream of extracted text segments.
    *   **States & Transitions:** Defines states (e.g., "InvoiceHeader", "LineItem") and transitions based on conditions (regex, coordinates, font properties).
    *   **Hierarchical Records:** Supports complex parent-child data structures (e.g., an Invoice record containing multiple LineItem records).
*   **Table Parsing:** specialized logic for grid-based data extraction based on column coordinates.
*   **Output Formats:** Exports structured data to CSV, JSON, XML, or flat JSON.
*   **Expression Engine:** Uses `expr` for complex logic in transition conditions (e.g., "if font is bold AND y-coordinate > 500").

### Architectural Highlights
*   **Pipeline Approach:** `Extractor` (PDF -> Text objects) -> `FsmParser` (Text -> StateValues) -> `RecordParser` (StateValues -> Records) -> `Output`.
*   **Config-Driven:** The extraction logic is entirely defined in declarative YAML files, decoupling code from document templates.
*   **Debuggability:** Extensive logging of state transitions and text analysis helps users debug why a specific field wasn't captured.

---

## 2. Strategic Ideas for Golden Armada

The "Golden Armada" needs to ingest vast amounts of "Dark Data" (PDFs, reports, forms) into SurrealDB. While LLMs (Gemini) are great at unstructured text, they are slow and expensive for high-volume, repetitive structure extraction. Textricator offers a deterministic, high-speed alternative for known document types.

### A. The "Schematic Ingestor" Pattern
Instead of throwing every PDF at Gemini, we define **Schematics** (YAML configs) for common document types.
*   **Idea:** Create a library of Textricator YAML configs stored in SurrealDB.
*   **Benefit:** Zero-hallucination extraction for financial documents, government forms, and technical datasheets.
*   **Hybrid Flow:** Use Textricator to extract the "Skeleton" (tables, headers) and pass specific extracted text blocks to Gemini for "Semantic Enrichment" (summarization, sentiment).

### B. Spatial-Semantic Indexing
Textricator extracts *where* text is. We can store this spatial metadata in SurrealDB.
*   **Idea:** Store document chunks with `(page, ulx, uly, lrx, lry)` coordinates.
*   **Benefit:** Enables "Visual QA". When an agent answers a question, it can highlight the exact bounding box on the original PDF overlay in the UI.

### C. FSM as a "Parser Agent" Tool
The FSM logic is effectively a "deterministic agent" that reads a document linearly.
*   **Idea:** Wrap Textricator as an MCP Tool. An Agno agent can write a YAML config on-the-fly (or select one) to parse a document it encounters.

---

## 3. Integration Plan (Agno + SurrealDB + Gemini 3)

We will integrate Textricator functionalities not by porting the Kotlin code, but by adopting its **Concepts** into a Python-based MCP server or by wrapping the JAR in a Docker container controlled by an MCP tool. Given the stack (Python/Agno), porting the *logic* or wrapping the CLI is preferred.

### Component: `DocumentIngestSquad`

#### 1. The `Schematic` Table (SurrealDB)
Store extraction configurations.
```sql
DEFINE TABLE schematic SCHEMAFULL;
DEFINE FIELD name ON TABLE schematic TYPE string;
DEFINE FIELD yaml_config ON TABLE schematic TYPE string; -- The Textricator YAML
DEFINE FIELD target_record_type ON TABLE schematic TYPE string;
```

#### 2. The `TextricatorTool` (MCP)
Since Textricator is a CLI tool, we can wrap it.
*   **Function:** `extract_structure(file_path: str, schematic_name: str)`
*   **Implementation:**
    1.  Agent requests extraction.
    2.  Tool fetches YAML from `schematic` table.
    3.  Tool runs `textricator.jar` (or a Python equivalent port) against the PDF using the config.
    4.  Output JSON is returned to the Agent.

#### 3. The `Refinery` Flow (Live Queries)
Use SurrealDB Live Queries to orchestrate the hybrid pipeline.

1.  **Ingest:** A PDF is uploaded. `App` creates a `document` record.
2.  **Classify (Gemini):** A lightweight agent sees the new `document`. It asks Gemini: "What type of document is this? Does it match any known Schematics?"
3.  **Route:**
    *   *If Match:* Update `document.processing_mode = 'textricator'`.
    *   *If Unknown:* Update `document.processing_mode = 'general_ocr'`.
4.  **Extract (Textricator):** A worker listening for `textricator` mode runs the CLI tool. It inserts structured data into `document.extracted_data`.
5.  **Enrich (Gemini):** A final pass where Gemini reads `document.extracted_data` and adds a `summary` or `embedding` for vector search.

### Adaptation: Python "PyTextricator"
Since the Golden Armada is Python-centric, we might eventually implement a simplified version of the FSM logic in Python (`PyMuPDF` + `Agno` FSM) to avoid the Java dependency, but keeping the *YAML Configuration Schema* is valuable for portability.

**Proposed Python Implementation using Agno:**
Instead of a strict YAML FSM, we use an Agno Agent with a specific "Reading Protocol".
*   **Input:** List of text blocks with coordinates.
*   **Prompt:** "You are a parser. Here is the layout of page 1. Extract the Invoice Number found near the top right..."
*   *Optimization:* For strict formats, we stick to the Java CLI wrapper for speed.

### Integration Workflow
1.  **User** uploads `invoice.pdf`.
2.  **ClassifierAgent** identifies it as "Standard Invoice Type A".
3.  **ExtractionAgent** calls `TextricatorTool` with `invoice_type_a.yaml`.
4.  **Textricator** outputs JSON: `{"total": 500.00, "date": "2023-10-01"}`.
5.  **SurrealDB** stores this in the `knowledge_graph`.
6.  **User** asks "How much did we spend in October?" -> **GraphRAG** queries the structured data directly, getting a perfect answer (no vector search fuzziness needed).
