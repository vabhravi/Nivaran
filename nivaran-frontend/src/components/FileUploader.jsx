/**
 * NIVARAN — FileUploader Component
 * Drag-and-drop file upload with visual feedback.
 * Supports PDF, PNG, JPG, JPEG, WebP.
 */

import React, { useState, useRef } from 'react';

const ALLOWED_TYPES = [
  'application/pdf',
  'image/png',
  'image/jpeg',
  'image/webp',
  'image/gif',
  'image/bmp',
  'image/tiff',
];

const ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'tiff', 'tif'];

function FileUploader({ onFileSelect, disabled, acceptLabel }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const inputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (disabled) return;

    const file = e.dataTransfer.files[0];
    if (file && isValidFile(file)) {
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  const handleClick = () => {
    if (!disabled && inputRef.current) {
      inputRef.current.click();
    }
  };

  const handleInputChange = (e) => {
    const file = e.target.files[0];
    if (file && isValidFile(file)) {
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  const isValidFile = (file) => {
    const ext = file.name.split('.').pop().toLowerCase();
    return ALLOWED_EXTENSIONS.includes(ext);
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div
      className={`file-uploader ${dragOver ? 'drag-over' : ''} ${disabled ? 'disabled' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
      id="file-uploader"
      role="button"
      tabIndex={0}
      aria-label="Upload document"
    >
      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_EXTENSIONS.map(e => `.${e}`).join(',')}
        onChange={handleInputChange}
        style={{ display: 'none' }}
        id="file-input"
        disabled={disabled}
      />

      <span className="file-uploader-icon">📄</span>
      <p className="file-uploader-text">
        {acceptLabel || 'Drag & drop your document here, or click to browse'}
      </p>
      <p className="file-uploader-hint">
        Supports: PDF, PNG, JPG, WebP &bull; Max 16 MB
      </p>

      {selectedFile && (
        <div className="file-uploader-selected">
          <span>📎</span>
          <div>
            <strong>{selectedFile.name}</strong>
            <span style={{ marginLeft: '8px', color: 'var(--text-tertiary)', fontSize: '0.85rem' }}>
              ({formatFileSize(selectedFile.size)})
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default FileUploader;
