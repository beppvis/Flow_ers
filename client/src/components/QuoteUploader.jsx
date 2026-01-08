import React, { useState, useRef, useCallback } from 'react';
import axios from 'axios';
import './QuoteUploader.css';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/jpg',
    'text/plain',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
];

const ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.txt', '.xls', '.xlsx', '.doc', '.docx'];

const QuoteUploader = () => {
    const [files, setFiles] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState({});
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // New state for Review Flow
    const [parsedItems, setParsedItems] = useState([]);
    const [isReviewing, setIsReviewing] = useState(false);
    const [isSyncing, setIsSyncing] = useState(false);
    const [syncResults, setSyncResults] = useState(null);

    const fileInputRef = useRef(null);

    // ... (File validation and drag-drop logic remains same, omitting for brevity in diff but assuming kept if I replace specific parts. 
    // Actually, replacing the whole component logic is safer to ensure state consistency)

    // Validate file before adding
    const validateFile = (file) => {
        const errors = [];
        if (file.size > MAX_FILE_SIZE) errors.push(`${file.name}: File size exceeds 10MB limit`);
        if (!ALLOWED_TYPES.includes(file.type)) errors.push(`${file.name}: Invalid file type`);
        return errors;
    };

    const handleFileSelect = useCallback((selectedFiles) => {
        // ... (Existing logic)
        const fileArray = Array.from(selectedFiles);
        const validFiles = fileArray.filter(file => validateFile(file).length === 0);
        setFiles(prev => [...prev, ...validFiles].slice(0, 5));
        setError(null);
    }, []);

    // ... Drag handlers ...
    const handleDragEnter = (e) => { e.preventDefault(); setIsDragging(true); };
    const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false); };
    const handleDrop = (e) => {
        e.preventDefault(); setIsDragging(false);
        if (e.dataTransfer.files.length > 0) handleFileSelect(e.dataTransfer.files);
    };

    const removeFile = (index) => {
        setFiles(files.filter((_, i) => i !== index));
    };

    // 1. UPLOAD -> PARSE
    const handleParse = async () => {
        if (files.length === 0) return;
        setIsUploading(true);
        setError(null);

        const formData = new FormData();
        files.forEach(file => formData.append('quotes', file));

        try {
            const response = await axios.post('/api/parse', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                onUploadProgress: (ev) => setUploadProgress({ overall: Math.round((ev.loaded * 100) / ev.total) })
            });

            if (response.data.success) {
                setParsedItems(response.data.data);
                setIsReviewing(true); // Switch to Review Mode
                setFiles([]);
            }
        } catch (err) {
            setError(err.response?.data?.detail || "Parsing failed.");
        } finally {
            setIsUploading(false);
            setUploadProgress({});
        }
    };

    // 2. EXPORT CSV
    const handleExportCSV = () => {
        if (parsedItems.length === 0) return;

        // Headers
        const headers = ["Item Code", "Name", "Group", "UOM", "Rate", "Description"];
        const rows = parsedItems.map(item => [
            item.item_code,
            item.item_name,
            item.item_group,
            item.stock_uom,
            item.standard_rate,
            `"${(item.description || '').replace(/"/g, '""')}"` // Escape quotes
        ]);

        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'extracted_items.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // 3. SYNC TO ERPNEXT
    const handleSync = async () => {
        setIsSyncing(true);
        try {
            const response = await axios.post('/api/insert', parsedItems);
            if (response.data.success) {
                setSyncResults(response.data.results);
                setSuccess("Items synced successfully!");
            }
        } catch (err) {
            setError("Sync failed: " + (err.response?.data?.detail || err.message));
        } finally {
            setIsSyncing(false);
        }
    };

    const handleReset = () => {
        setFiles([]);
        setParsedItems([]);
        setIsReviewing(false);
        setSuccess(null);
        setError(null);
        setSyncResults(null);
    };

    // RENDER: REVIEW TABLE
    if (isReviewing) {
        return (
            <div className="quote-uploader review-mode">
                <div className="uploader-card full-width">
                    <div className="card-header">
                        <h2>Review Extracted Data</h2>
                        <button className="close-btn" onClick={handleReset}>Close</button>
                    </div>

                    {success && <div className="message success">✓ {success}</div>}
                    {error && <div className="message error">! {error}</div>}

                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Item Code</th>
                                    <th>Name</th>
                                    <th>Group</th>
                                    <th>UOM</th>
                                    <th>Rate</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {parsedItems.map((item, idx) => {
                                    const syncStatus = syncResults ? syncResults.find(r => r.item_code === item.item_code) : null;
                                    return (
                                        <tr key={idx} className={syncStatus ? syncStatus.status : ''}>
                                            <td>{item.item_code}</td>
                                            <td>{item.item_name}</td>
                                            <td>{item.item_group}</td>
                                            <td>{item.stock_uom}</td>
                                            <td>{item.standard_rate}</td>
                                            <td>
                                                {syncStatus ? (
                                                    <span className={`status-badge ${syncStatus.status}`}>
                                                        {syncStatus.status === 'success' ? 'Synced' : 'Failed'}
                                                    </span>
                                                ) : '-'}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>

                    <div className="actions-footer">
                        <button className="secondary-btn" onClick={handleExportCSV}>
                            ⬇ Export CSV
                        </button>
                        <button className="primary-btn" onClick={handleSync} disabled={isSyncing || !!syncResults}>
                            {isSyncing ? 'Syncing...' : (syncResults ? 'Synced' : 'Cloud Sync to ERPNext')}
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // RENDER: UPLOAD FORM (Default)
    return (
        <div className="quote-uploader">
            <div className="uploader-card">
                <h2>Upload Quote Files</h2>
                <div
                    className={`drop-zone ${isDragging ? 'dragging' : ''}`}
                    onDragEnter={handleDragEnter}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                >
                    <input
                        ref={fileInputRef} type="file" multiple
                        accept=".pdf,.xlsx,.jpg,.png"
                        onChange={(e) => handleFileSelect(e.target.files)}
                        style={{ display: 'none' }}
                    />
                    <p>{isDragging ? "Drop files now" : "Click / Drag files here"}</p>
                </div>

                {isUploading && <div className="progress">Parsing... {uploadProgress.overall}%</div>}

                <div className="file-list">
                    {files.map((f, i) => (
                        <div key={i} className="file-item">
                            <span>{f.name}</span>
                            <button onClick={(e) => { e.stopPropagation(); removeFile(i); }}>×</button>
                        </div>
                    ))}
                </div>

                <button
                    className="upload-btn"
                    disabled={files.length === 0 || isUploading}
                    onClick={handleParse}
                >
                    {isUploading ? 'Processing...' : 'Process Files'}
                </button>

                {error && <div className="message error">{error}</div>}
            </div>
        </div>
    );
};

export default QuoteUploader;

