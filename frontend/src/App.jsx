import { useMemo, useState } from 'react';

import { apiBase } from './config/runtime.js';

const STEPS = [
  'Lecture CSV',
  'Analyse',
  'Regroupement',
  'Creation PDF',
  'Compression ZIP'
];

export default function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [colorMode, setColorMode] = useState('black_and_white');
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const currentScreen = useMemo(() => {
    if (result) {
      return 4;
    }
    if (isGenerating) {
      return 3;
    }
    if (analysis) {
      return 2;
    }
    return 1;
  }, [analysis, isGenerating, result]);

  async function analyzeSelectedFile(selectedFile) {
    setFile(selectedFile);
    setAnalysis(null);
    setResult(null);
    setError('');
    setIsAnalyzing(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      const response = await fetch(`${apiBase}/api/csv/analyze`, {
        method: 'POST',
        body: formData
      });
      const payload = await readJsonResponse(response);
      setAnalysis(payload);
    } catch (apiError) {
      setError(apiError.message);
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function generateZip() {
    if (!file) {
      return;
    }

    setError('');
    setResult(null);
    setIsGenerating(true);
    setCompletedSteps([]);

    try {
      for (const step of STEPS.slice(0, 3)) {
        await markStep(step);
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('color_mode', colorMode);

      const response = await fetch(`${apiBase}/api/generate`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(await readError(response));
      }

      await markStep('Creation PDF');
      const zipBlob = await response.blob();
      await markStep('Compression ZIP');

      const downloadUrl = URL.createObjectURL(zipBlob);
      setResult({
        downloadUrl,
        fileName: 'jira-cards.zip',
        cardCount: Number(response.headers.get('X-Card-Count') || 0),
        pageCount: Number(response.headers.get('X-Page-Count') || 0),
        pdfCount: Number(response.headers.get('X-Pdf-Count') || 0)
      });
    } catch (apiError) {
      setError(apiError.message);
    } finally {
      setIsGenerating(false);
    }
  }

  function handleDrop(event) {
    event.preventDefault();
    setIsDragging(false);
    const selectedFile = event.dataTransfer.files?.[0];
    if (selectedFile) {
      analyzeSelectedFile(selectedFile);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Portail applications</p>
          <h1>Cartes Jira</h1>
          <p className="lead">Generation deterministe de cartes imprimables depuis un export CSV Jira.</p>
        </div>
        <span className="status-pill">Etape {currentScreen}/4</span>
      </header>

      {error ? <div className="alert-box">{error}</div> : null}

      <section className="panel workspace-panel">
        {currentScreen === 1 ? (
          <ImportScreen
            file={file}
            isAnalyzing={isAnalyzing}
            isDragging={isDragging}
            onDragState={setIsDragging}
            onDrop={handleDrop}
            onSelectFile={analyzeSelectedFile}
          />
        ) : null}

        {currentScreen === 2 ? (
          <SummaryScreen
            analysis={analysis}
            colorMode={colorMode}
            file={file}
            onGenerate={generateZip}
            onReset={() => {
              setFile(null);
              setAnalysis(null);
              setResult(null);
            }}
            onSetColorMode={setColorMode}
          />
        ) : null}

        {currentScreen === 3 ? (
          <ProgressScreen completedSteps={completedSteps} />
        ) : null}

        {currentScreen === 4 ? (
          <ResultScreen
            result={result}
            onReset={() => {
              setFile(null);
              setAnalysis(null);
              setResult(null);
              setCompletedSteps([]);
            }}
          />
        ) : null}
      </section>
    </main>
  );

  async function markStep(step) {
    setCompletedSteps((currentSteps) => Array.from(new Set([...currentSteps, step])));
    await new Promise((resolve) => setTimeout(resolve, 170));
  }
}

function ImportScreen({
  file,
  isAnalyzing,
  isDragging,
  onDragState,
  onDrop,
  onSelectFile
}) {
  return (
    <div className="stack">
      <div className="section-heading">
        <div>
          <h2>Importer le CSV</h2>
          <p className="muted">Export Jira au format CSV.</p>
        </div>
      </div>

      <label
        className={`drop-zone ${isDragging ? 'is-dragging' : ''}`}
        onDragEnter={(event) => {
          event.preventDefault();
          onDragState(true);
        }}
        onDragOver={(event) => event.preventDefault()}
        onDragLeave={() => onDragState(false)}
        onDrop={onDrop}
      >
        <input
          accept=".csv,text/csv"
          type="file"
          onChange={(event) => {
            const selectedFile = event.target.files?.[0];
            if (selectedFile) {
              onSelectFile(selectedFile);
            }
          }}
        />
        <span className="drop-icon">CSV</span>
        <strong>{file ? file.name : 'Deposer le fichier ici'}</strong>
        <small>{isAnalyzing ? 'Analyse en cours...' : 'ou selectionner un fichier'}</small>
      </label>
    </div>
  );
}

function SummaryScreen({
  analysis,
  colorMode,
  file,
  onGenerate,
  onReset,
  onSetColorMode
}) {
  return (
    <div className="stack">
      <div className="section-heading">
        <div>
          <h2>Resume</h2>
          <p className="muted">{file?.name}</p>
        </div>
        <button className="secondary" type="button" onClick={onReset}>
          Changer de CSV
        </button>
      </div>

      <div className="info-grid">
        <InfoCard label="Tickets" value={analysis.ticket_count} />
        <InfoCard label="Features" value={analysis.feature_count} />
        <InfoCard label="Mode" value={colorMode === 'color' ? 'Couleur' : 'Noir et blanc'} />
      </div>

      <div className="choice-group">
        <label className={colorMode === 'black_and_white' ? 'choice-card selected' : 'choice-card'}>
          <input
            checked={colorMode === 'black_and_white'}
            name="colorMode"
            type="radio"
            value="black_and_white"
            onChange={() => onSetColorMode('black_and_white')}
          />
          <strong>Noir et blanc</strong>
          <span>Contour fin et reperes de coupe.</span>
        </label>
        <label className={colorMode === 'color' ? 'choice-card selected' : 'choice-card'}>
          <input
            checked={colorMode === 'color'}
            name="colorMode"
            type="radio"
            value="color"
            onChange={() => onSetColorMode('color')}
          />
          <strong>Couleur</strong>
          <span>Contour stable par Feature.</span>
        </label>
      </div>

      <div className="feature-table">
        <div className="feature-table-head">
          <span>Feature</span>
          <span>US</span>
          <span>Pages</span>
        </div>
        {analysis.feature_details.map((feature) => (
          <div className="feature-table-row" key={feature.key}>
            <div>
              <strong>{feature.key}</strong>
              <span>{feature.summary}</span>
            </div>
            <span className="pill">{feature.user_story_count}</span>
            <span className="pill">{feature.page_count}</span>
          </div>
        ))}
      </div>

      <div className="action-row">
        <button type="button" onClick={onGenerate}>Generer</button>
      </div>
    </div>
  );
}

function ProgressScreen({ completedSteps }) {
  return (
    <div className="stack">
      <div className="section-heading">
        <div>
          <h2>Generation</h2>
          <p className="muted">Preparation de l'archive ZIP.</p>
        </div>
      </div>
      <div className="progress-list">
        {STEPS.map((step) => (
          <div className={completedSteps.includes(step) ? 'progress-item done' : 'progress-item'} key={step}>
            <span>{completedSteps.includes(step) ? 'OK' : '...'}</span>
            <strong>{step}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

function ResultScreen({ result, onReset }) {
  return (
    <div className="stack">
      <div className="section-heading">
        <div>
          <h2>Archive prete</h2>
          <p className="muted">Les PDF sont regroupes dans un fichier ZIP.</p>
        </div>
      </div>

      <div className="info-grid">
        <InfoCard label="Cartes" value={result.cardCount} />
        <InfoCard label="Pages" value={result.pageCount} />
        <InfoCard label="PDF" value={result.pdfCount} />
      </div>

      <div className="action-row">
        <a className="button" href={result.downloadUrl} download={result.fileName}>
          Telecharger le ZIP
        </a>
        <button className="secondary" type="button" onClick={onReset}>
          Nouvelle generation
        </button>
      </div>
    </div>
  );
}

function InfoCard({ label, value }) {
  return (
    <div className="info-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

async function readJsonResponse(response) {
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json();
}

async function readError(response) {
  try {
    const payload = await response.json();
    return payload.detail || 'Une erreur est survenue.';
  } catch {
    return 'Une erreur est survenue.';
  }
}
