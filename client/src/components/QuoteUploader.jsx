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

function QuoteUploader() {
    const [files, setFiles] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState({});
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const fileInputRef = useRef(null);

    // Validate file before adding
    const validateFile = (file) => {
        const errors = [];

        // Check file size
        if (file.size > MAX_FILE_SIZE) {
            errors.push(`${file.name}: File size exceeds 10MB limit`);
        }

        // Check MIME type
        if (!ALLOWED_TYPES.includes(file.type)) {
            errors.push(`${file.name}: Invalid file type. Allowed: PDF, Images, Excel, Word, Text`);
        }

        // Check extension as additional validation
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!ALLOWED_EXTENSIONS.includes(extension)) {
            errors.push(`${file.name}: Invalid file extension`);
        }

        // Check for empty files
        if (file.size === 0) {
            errors.push(`${file.name}: File is empty`);
        }

        return errors;
    };

    // Handle file selection
    const handleFileSelect = useCallback((selectedFiles) => {
        setError(null);
        setSuccess(null);

        const fileArray = Array.from(selectedFiles);
        const allErrors = [];
        const validFiles = [];

        // Validate each file
        fileArray.forEach(file => {
            const errors = validateFile(file);
            if (errors.length > 0) {
                allErrors.push(...errors);
            } else {
                validFiles.push(file);
            }
        });

        if (allErrors.length > 0) {
            setError(allErrors.join('\n'));
        }

        // Add valid files (max 5 total)
        const newFiles = [...files, ...validFiles].slice(0, 5);
        setFiles(newFiles);

        if (newFiles.length >= 5) {
            setError(prev => prev ? prev + '\nMaximum 5 files allowed' : 'Maximum 5 files allowed');
        }
    }, [files]);

    // Drag and drop handlers
    const handleDragEnter = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    }, []);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const droppedFiles = e.dataTransfer.files;
        if (droppedFiles.length > 0) {
            handleFileSelect(droppedFiles);
        }
    }, [handleFileSelect]);

    // File input change handler
    const handleInputChange = (e) => {
        const selectedFiles = e.target.files;
        if (selectedFiles.length > 0) {
            handleFileSelect(selectedFiles);
        }
        // Reset input to allow selecting same file again
        e.target.value = '';
    };

    // Remove file from list
    const removeFile = (index) => {
        const newFiles = files.filter((_, i) => i !== index);
        setFiles(newFiles);
        setError(null);
    };

    // Format file size
    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    // Get file type icon
    const getFileIcon = (type) => {
        if (type.includes('pdf')) return '[PDF]';
        if (type.includes('image')) return '[IMG]';
        if (type.includes('excel') || type.includes('spreadsheet')) return '[XLS]';
        if (type.includes('word') || type.includes('document')) return '[DOC]';
        return '[FILE]';
    };

    // Upload files
    const handleUpload = async () => {
        if (files.length === 0) {
            setError('Please select at least one file to upload');
            return;
        }

        setIsUploading(true);
        setError(null);
        setSuccess(null);
        setUploadProgress({});

        const formData = new FormData();
        files.forEach(file => {
            formData.append('quotes', file);
        });

        try {
            const response = await axios.post('/api/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    setUploadProgress({ overall: percentCompleted });
                },
                timeout: 60000, // 60 second timeout
            });

            if (response.data.success) {
                setSuccess(response.data.message);
                setFiles([]);
                setUploadProgress({});
            }
        } catch (err) {
            let errorMessage = 'Upload failed. Please try again.';

            if (err.response) {
                // Server responded with error
                errorMessage = err.response.data?.error || errorMessage;
            } else if (err.request) {
                // Request made but no response
                errorMessage = 'Network error. Please check your connection.';
            } else if (err.code === 'ECONNABORTED') {
                errorMessage = 'Upload timeout. Please try again with smaller files.';
            }

            setError(errorMessage);
        } finally {
            setIsUploading(false);
            setUploadProgress({});
        }
    };

    return (
        <div className="quote-uploader">
            <div className="uploader-card">
                <h2>Upload Quote Files</h2>
                <p className="upload-description">
                    Drag and drop files here, or click to browse. Supports PDF, Images, Excel, Word, and Text files (Max 10MB each, up to 5 files).
                </p>

                {/* Drag and Drop Zone */}
                <div
                    className={`drop-zone ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
                    onDragEnter={handleDragEnter}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => !isUploading && fileInputRef.current?.click()}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        accept=".pdf,.jpg,.jpeg,.png,.txt,.xls,.xlsx,.doc,.docx"
                        onChange={handleInputChange}
                        style={{ display: 'none' }}
                        disabled={isUploading || files.length >= 5}
                    />

                    {isUploading ? (
                        <div className="upload-status">
                            <div className="spinner"></div>
                            <p>Uploading... {uploadProgress.overall || 0}%</p>
                        </div>
                    ) : (
                        <div className="drop-zone-content">
                            <div className="upload-icon">↑</div>
                            <p className="drop-zone-text">
                                {isDragging ? 'Drop files here' : 'Click or drag files here'}
                            </p>
                            <p className="drop-zone-hint">
                                PDF, Images, Excel, Word, Text (Max 10MB)
                            </p>
                        </div>
                    )}
                </div>

                {/* File List */}
                {files.length > 0 && (
                    <div className="file-list">
                        <h3>Selected Files ({files.length}/5)</h3>
                        {files.map((file, index) => (
                            <div key={index} className="file-item">
                                <span className="file-icon">{getFileIcon(file.type)}</span>
                                <div className="file-info">
                                    <p className="file-name">{file.name}</p>
                                    <p className="file-details">
                                        {formatFileSize(file.size)} • {file.type || 'Unknown type'}
                                    </p>
                                </div>
                                <button
                                    className="remove-btn"
                                    onClick={() => removeFile(index)}
                                    disabled={isUploading}
                                    aria-label="Remove file"
                                >
                                    ×
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Error Message */}
                {error && (
                    <div className="message error">
                        <span className="message-icon">!</span>
                        <div className="message-content">
                            <strong>Error:</strong>
                            <pre>{error}</pre>
                        </div>
                    </div>
                )}

                {/* Success Message */}
                {success && (
                    <div className="message success">
                        <span className="message-icon">✓</span>
                        <div className="message-content">
                            <strong>Success:</strong> {success}
                        </div>
                    </div>
                )}

                {/* Upload Button */}
                <button
                    className="upload-btn"
                    onClick={handleUpload}
                    disabled={files.length === 0 || isUploading}
                >
                    {isUploading ? 'Uploading...' : `Upload ${files.length} File${files.length !== 1 ? 's' : ''}`}
                </button>
            </div>
        </div>
    );
}

export default QuoteUploader;

