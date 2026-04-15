import React, { useRef, useState, useCallback } from 'react';

/**
 * Photo/video file picker with drag-and-drop support.
 */
export function PhotoPicker({ onFilesSelected, disabled = false }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedCount, setSelectedCount] = useState(0);

  const handleFiles = useCallback(
    (fileList) => {
      if (!fileList || fileList.length === 0) return;

      // Filter to only images and videos
      const validTypes = /^(image|video)\//;
      const files = Array.from(fileList).filter(
        (f) => validTypes.test(f.type) || /\.(jpg|jpeg|png|gif|webp|heic|heif|mp4|mov|avi|mkv|3gp)$/i.test(f.name)
      );

      setSelectedCount(files.length);
      onFilesSelected?.(files);
    },
    [onFilesSelected]
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setIsDragging(false);
      if (disabled) return;
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles, disabled]
  );

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleClick = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleChange = (e) => {
    handleFiles(e.target.files);
  };

  return (
    <div id="photo-picker">
      <div
        className={`drop-zone ${isDragging ? 'drop-zone--active' : ''} ${disabled ? '' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
        style={{ opacity: disabled ? 0.5 : 1, pointerEvents: disabled ? 'none' : 'auto' }}
      >
        <div className="drop-zone__icon">📸</div>
        <p className="drop-zone__text">
          <strong>Tap to select photos & videos</strong>
          <br />
          or drag and drop here
        </p>
        <input
          ref={inputRef}
          type="file"
          accept="image/*,video/*"
          multiple
          onChange={handleChange}
          id="file-input"
        />
      </div>

      {selectedCount > 0 && (
        <div className="text-center mt-2">
          <div className="file-count-badge">
            📁 <span>{selectedCount}</span> file{selectedCount !== 1 ? 's' : ''} selected
          </div>
        </div>
      )}
    </div>
  );
}
