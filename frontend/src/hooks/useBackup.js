import { useState, useCallback, useRef } from 'react';
import { computeSHA256 } from '../utils/hash';
import { getDiff, initUpload, uploadChunk, completeUpload } from '../api/client';

const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB chunks

/**
 * Hook that orchestrates the full backup pipeline:
 * 1. Hash all files client-side (SHA-256)
 * 2. Send diff to server to determine which files are new
 * 3. Upload each new file in chunks
 * 4. Track progress throughout
 */
export function useBackup() {
  const [status, setStatus] = useState('idle'); // idle | hashing | diffing | uploading | complete | error
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState('');
  const [speed, setSpeed] = useState(0);
  const [eta, setEta] = useState(0);
  const [filesTotal, setFilesTotal] = useState(0);
  const [filesDone, setFilesDone] = useState(0);
  const [skipped, setSkipped] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');

  const abortRef = useRef(false);

  const startBackup = useCallback(async (files) => {
    if (!files || files.length === 0) return;

    abortRef.current = false;
    setStatus('hashing');
    setProgress(0);
    setFilesDone(0);
    setSkipped(0);
    setErrorMessage('');
    setFilesTotal(files.length);

    try {
      // Step 1: Hash all files
      const fileInfos = [];
      for (let i = 0; i < files.length; i++) {
        if (abortRef.current) throw new Error('Backup cancelled');
        const file = files[i];
        setCurrentFile(`Hashing: ${file.name}`);
        setProgress(Math.round(((i + 1) / files.length) * 30)); // 0-30% for hashing

        const sha256 = await computeSHA256(file);
        fileInfos.push({
          file,
          filename: file.name,
          sha256,
          size: file.size,
        });
      }

      // Step 2: Diff with server
      setStatus('diffing');
      setCurrentFile('Checking for duplicates…');
      setProgress(32);

      const diffResult = await getDiff(
        fileInfos.map((f) => ({
          filename: f.filename,
          sha256: f.sha256,
          size: f.size,
        }))
      );

      const knownSet = new Set(diffResult.known);
      const filesToUpload = fileInfos.filter((f) => !knownSet.has(f.sha256));
      const skippedCount = fileInfos.length - filesToUpload.length;
      setSkipped(skippedCount);

      if (filesToUpload.length === 0) {
        setStatus('complete');
        setProgress(100);
        setCurrentFile('All files already backed up!');
        setFilesDone(files.length);
        return;
      }

      // Step 3: Upload each new file
      setStatus('uploading');
      const uploadStart = Date.now();
      let totalBytesUploaded = 0;
      const totalBytesToUpload = filesToUpload.reduce((s, f) => s + f.size, 0);

      for (let i = 0; i < filesToUpload.length; i++) {
        if (abortRef.current) throw new Error('Backup cancelled');

        const { file, filename, sha256 } = filesToUpload[i];
        setCurrentFile(filename);

        const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

        // Init upload session
        const session = await initUpload({
          filename,
          totalChunks,
          totalSize: file.size,
          sha256,
          mimeType: file.type || 'application/octet-stream',
        });

        // Upload chunks
        for (let c = 0; c < totalChunks; c++) {
          if (abortRef.current) throw new Error('Backup cancelled');

          const start = c * CHUNK_SIZE;
          const end = Math.min(start + CHUNK_SIZE, file.size);
          const blob = file.slice(start, end);

          await uploadChunk(session.upload_id, c, blob);

          totalBytesUploaded += end - start;

          // Calculate speed and ETA
          const elapsed = (Date.now() - uploadStart) / 1000;
          const currentSpeed = totalBytesUploaded / elapsed;
          const remaining = totalBytesToUpload - totalBytesUploaded;
          const estimatedTime = remaining / currentSpeed;

          setSpeed(currentSpeed);
          setEta(Math.round(estimatedTime));

          // Progress: 35-95% for uploading
          const uploadProgress = totalBytesUploaded / totalBytesToUpload;
          setProgress(Math.round(35 + uploadProgress * 60));
        }

        // Complete upload
        await completeUpload(session.upload_id);
        setFilesDone(skippedCount + i + 1);
      }

      // Done!
      setStatus('complete');
      setProgress(100);
      setCurrentFile('Backup complete!');
      setFilesDone(files.length);
      setSpeed(0);
      setEta(0);
    } catch (err) {
      if (err.message === 'Backup cancelled') {
        setStatus('idle');
        setCurrentFile('');
      } else {
        setStatus('error');
        setErrorMessage(err.message);
        setCurrentFile(`Error: ${err.message}`);
      }
    }
  }, []);

  const cancelBackup = useCallback(() => {
    abortRef.current = true;
  }, []);

  const reset = useCallback(() => {
    setStatus('idle');
    setProgress(0);
    setCurrentFile('');
    setSpeed(0);
    setEta(0);
    setFilesTotal(0);
    setFilesDone(0);
    setSkipped(0);
    setErrorMessage('');
    abortRef.current = false;
  }, []);

  return {
    startBackup,
    cancelBackup,
    reset,
    status,
    progress,
    currentFile,
    speed,
    eta,
    filesTotal,
    filesDone,
    skipped,
    errorMessage,
  };
}
