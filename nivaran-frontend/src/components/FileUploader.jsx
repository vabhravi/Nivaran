/**
 * NIVARAN — FileUploader Component (v2)
 * Premium drag-and-drop file upload with animated borders,
 * file type detection, and micro-animations.
 */

import React, { useState, useRef } from 'react';

const ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'tiff', 'tif'];

function FileUploader({ onFileSelect, disabled, acceptLabel }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [justDropped, setJustDropped] = useState(false);
  const inputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (disabled) return;

    const file = e.dataTransfer.files[0];
    if (file && isValidFile(file)) {
      selectFile(file);
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
      selectFile(file);
    }
  };

  const selectFile = (file) => {
    setSelectedFile(file);
    setJustDropped(true);
    onFileSelect(file);
    setTimeout(() => setJustDropped(false), 600);
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

  const getFileIcon = (filename) => {
    if (!filename) return '📄';
    const ext = filename.split('.').pop().toLowerCase();
    if (ext === 'pdf') return '📑';
    if (['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'].includes(ext)) return '🖼️';
    return '📄';
  };

  return (
    <div
      className={`file-uploader-v2 ${dragOver ? 'drag-over' : ''} ${disabled ? 'disabled' : ''} ${justDropped ? 'just-dropped' : ''} ${selectedFile ? 'has-file' : ''}`}
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

      {/* Animated border decoration */}
      <div className="file-uploader-v2-border" />

      {/* Upload content */}
      <div className="file-uploader-v2-content">
        {selectedFile ? (
          <>
            <div className="file-uploader-v2-success">
              <span className="file-uploader-v2-check">✓</span>
            </div>
            <div className="file-uploader-v2-file-info">
              <span className="file-uploader-v2-file-icon">{getFileIcon(selectedFile.name)}</span>
              <div>
                <p className="file-uploader-v2-filename">{selectedFile.name}</p>
                <p className="file-uploader-v2-filesize">{formatFileSize(selectedFile.size)}</p>
              </div>
            </div>
            <p className="file-uploader-v2-change">Click to change file</p>
          </>
        ) : (
          <>
            <div className="file-uploader-v2-icon-wrap">
              <span className="file-uploader-v2-icon">
                {dragOver ? '📥' : '📄'}
              </span>
            </div>
            <p className="file-uploader-v2-text">
              {acceptLabel || 'Drop your rental agreement here, or click to browse'}
            </p>
            <p className="file-uploader-v2-hint">
              Supports PDF, PNG, JPG, WebP &bull; Max 16 MB
            </p>
            <div className="file-uploader-v2-formats">
              <span className="file-uploader-v2-format-tag">📑 PDF</span>
              <span className="file-uploader-v2-format-tag">🖼️ PNG</span>
              <span className="file-uploader-v2-format-tag">🖼️ JPG</span>
              <span className="file-uploader-v2-format-tag">🖼️ WebP</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default FileUploader;
