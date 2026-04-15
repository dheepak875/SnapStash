import React, { useState } from 'react';
import { WelcomeScreen } from './components/WelcomeScreen';
import { BackupView } from './components/BackupView';

/**
 * SnapStash — Root Application
 * Simple state machine: welcome → backup
 */
export default function App() {
  const [view, setView] = useState('welcome'); // 'welcome' | 'backup'

  return (
    <div className="container">
      {/* Header */}
      <header className="app-header anim-slide-up">
        <h1 className="app-logo">SnapStash</h1>
        <p className="app-tagline">Private Photo Cloud</p>
      </header>

      {/* Views */}
      {view === 'welcome' && (
        <WelcomeScreen onContinue={() => setView('backup')} />
      )}

      {view === 'backup' && (
        <BackupView onBack={() => setView('welcome')} />
      )}
    </div>
  );
}
