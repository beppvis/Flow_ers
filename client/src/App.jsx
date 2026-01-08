import React from 'react';
import QuoteUploader from './components/QuoteUploader';
import './App.css';

function App() {
    return (
        <div className="app">
            <header className="app-header">
                <div className="container">
                    <h1>Quote Processor</h1>
                    <p className="subtitle">Automated Quote Processor for Logistics</p>
                    <p className="tagline">Build2Break Hackathon - LogiTech Domain</p>
                </div>
            </header>
            <main className="app-main">
                <div className="container">
                    <QuoteUploader />
                </div>
            </main>
            <footer className="app-footer">
                <div className="container">
                    <p>Upload quotes in PDF, Images, Excel, Word, or Text formats</p>
                </div>
            </footer>
        </div>
    );
}

export default App;

