import { useMemo, useState } from 'react';

import { apiBase } from './config/runtime.js';

const STEPS = [
  'Lecture CSV',
  'Analyse',
  'Regroupement',
  'Création PDF',
  'Compression ZIP'
];

export default function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [colorMode, setColorMode] = useState('black_and_white');
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [colorVariant, setColorVariant] = useState(0);
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

  async function analyzeSelectedFile(selectedFile, nextColorVariant = colorVariant, options = {}) {
    setFile(selectedFile);
    if (!options.keepAnalysis) {
      setAnalysis(null);
    }
    setResult(null);
    setError('');
    setIsAnalyzing(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('color_variant', String(nextColorVariant));
      const response = await fetch(`${apiBase}/api/csv/analyze`, {
        method: 'POST',
        body: formData
      });
      const payload = await readJsonResponse(response);
      setColorVariant(payload.color_variant ?? nextColorVariant);
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
      formData.append('color_variant', String(colorVariant));

      const response = await fetch(`${apiBase}/api/generate`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(await readError(response));
      }

      await markStep('Création PDF');
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

  function regenerateColors() {
    if (!file || isAnalyzing || isGenerating) {
      return;
    }
    const nextColorVariant = colorVariant + 1;
    setColorVariant(nextColorVariant);
    analyzeSelectedFile(file, nextColorVariant, { keepAnalysis: true });
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Portail applications</p>
          <h1>Cartes Jira</h1>
          <p className="lead">Génération de cartes imprimables depuis un export CSV Jira.</p>
        </div>
        <span className="status-pill">Étape {currentScreen}/4</span>
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
            onOpenHelp={() => setIsHelpOpen(true)}
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
              setColorVariant(0);
            }}
            onRegenerateColors={regenerateColors}
            onSetColorMode={setColorMode}
            isAnalyzing={isAnalyzing}
            isGenerating={isGenerating}
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
              setColorVariant(0);
            }}
          />
        ) : null}
      </section>

      {isHelpOpen ? <HelpModal onClose={() => setIsHelpOpen(false)} /> : null}
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
  onOpenHelp,
  onSelectFile
}) {
  return (
    <div className="stack">
      <div className="section-heading">
        <div>
          <h2>Importer le CSV</h2>
          <p className="muted">Export Jira au format CSV.</p>
        </div>
        <button className="secondary" type="button" onClick={onOpenHelp}>
          Mode opératoire
        </button>
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
        <strong>{file ? file.name : 'Déposer le fichier ici'}</strong>
        <small>{isAnalyzing ? 'Analyse en cours...' : 'ou sélectionner un fichier'}</small>
      </label>
    </div>
  );
}

function HelpModal({ onClose }) {
  return (
    <div
      aria-labelledby="help-modal-title"
      aria-modal="true"
      className="modal-backdrop"
      role="dialog"
    >
      <div className="modal-panel">
        <div className="modal-header">
          <div>
            <p className="eyebrow">Aide</p>
            <h2 id="help-modal-title">Comment générer vos cartes Jira ?</h2>
          </div>
          <button className="secondary icon-button" type="button" aria-label="Fermer" onClick={onClose}>
            X
          </button>
        </div>

        <div className="help-steps">
          <section>
            <h3>1. Préparez votre recherche dans Jira</h3>
            <p>
              Ouvrez le{' '}
              <a href="https://bgpn.atlassian.net/issues/?filter=32318" target="_blank" rel="noreferrer">
                filtre Jira proposé
              </a>
              , puis adaptez si nécessaire les critères à votre besoin : Espace, Type de ticket,
              Composant, Sprint...
            </p>
          </section>

          <section>
            <h3>2. Vérifiez les colonnes</h3>
            <p>Affichez au minimum les colonnes suivantes :</p>
            <p className="help-highlight">Clé de ticket - Résumé - Story Point - Parent</p>
          </section>

          <section>
            <h3>3. Exportez votre recherche</h3>
            <p>Dans Jira, sélectionnez :</p>
            <p className="help-highlight">CSV - mes champs par défaut</p>
            <p>Enregistrez ensuite le fichier .csv sur votre ordinateur.</p>
          </section>

          <section>
            <h3>4. Importez le fichier</h3>
            <p>Dans l'application, sélectionnez ou déposez votre fichier CSV dans la zone prévue à cet effet.</p>
          </section>

          <section>
            <h3>5. Générez vos cartes</h3>
            <p>Vérifiez le jeu de couleurs proposé.</p>
            <p>Les couleurs ne vous conviennent pas ? Cliquez sur Autres couleurs pour obtenir une nouvelle proposition.</p>
            <p>Lorsque tout vous convient, cliquez sur Générer.</p>
            <p className="help-highlight">Vos cartes Jira sont prêtes !</p>
          </section>
        </div>

        <div className="modal-actions">
          <button type="button" onClick={onClose}>Compris</button>
        </div>
      </div>
    </div>
  );
}

function SummaryScreen({
  analysis,
  colorMode,
  file,
  isAnalyzing,
  isGenerating,
  onGenerate,
  onRegenerateColors,
  onReset,
  onSetColorMode
}) {
  const featureDetails = Array.isArray(analysis.feature_details)
    ? analysis.feature_details
    : (analysis.features || []).map((feature) => ({
        key: feature,
        summary: '',
        label: feature,
        color: '#000000',
        user_story_count: '-',
        page_count: '-'
      }));
  const totalPages = featureDetails.reduce((total, feature) => {
    const pageCount = Number(feature.page_count);
    return Number.isFinite(pageCount) ? total + pageCount : total;
  }, 0);

  return (
    <div className="stack">
      <div className="section-heading">
        <div>
          <h2>Résumé</h2>
          <p className="muted">{file?.name}</p>
        </div>
        <button className="secondary" type="button" onClick={onReset}>
          Changer de CSV
        </button>
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
          <span>Contour fin et repères de coupe.</span>
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
          <span>Feature ({analysis.feature_count})</span>
          <span>Couleur</span>
          <span>US ({analysis.ticket_count})</span>
          <span>Pages ({totalPages})</span>
        </div>
        {featureDetails.map((feature) => (
          <div className="feature-table-row" key={feature.label || feature.key}>
            <div>
              <strong>{feature.key}</strong>
              {feature.summary ? <span>{feature.summary}</span> : null}
            </div>
            <span className="color-cell">
              <span
                aria-hidden="true"
                className="color-swatch"
                style={{ backgroundColor: feature.color || '#000000' }}
              />
              <span>{feature.color || '-'}</span>
            </span>
            <span className="pill">{feature.user_story_count}</span>
            <span className="pill">{feature.page_count}</span>
          </div>
        ))}
      </div>

      <div className="action-row">
        <button
          className="secondary"
          disabled={isAnalyzing || isGenerating}
          type="button"
          onClick={onRegenerateColors}
        >
          Autres couleurs
        </button>
        <button type="button" onClick={onGenerate}>Générer</button>
      </div>
    </div>
  );
}

function ProgressScreen({ completedSteps }) {
  return (
    <div className="stack">
      <div className="section-heading">
        <div>
          <h2>Génération</h2>
          <p className="muted">Préparation de l'archive ZIP.</p>
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
          <h2>Archive prête</h2>
          <p className="muted">Les PDF sont regroupés dans un fichier ZIP.</p>
        </div>
      </div>

      <div className="info-grid">
        <InfoCard label="Cartes" value={result.cardCount} />
        <InfoCard label="Pages" value={result.pageCount} />
        <InfoCard label="PDF" value={result.pdfCount} />
      </div>

      <div className="action-row">
        <a className="button" href={result.downloadUrl} download={result.fileName}>
          Télécharger le ZIP
        </a>
        <button className="secondary" type="button" onClick={onReset}>
          Nouvelle génération
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
