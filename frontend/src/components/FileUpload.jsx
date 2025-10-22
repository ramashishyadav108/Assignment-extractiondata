import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';

const FileUpload = ({ onFilesSelected, disabled }) => {
  const [files, setFiles] = useState([]);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    if (rejectedFiles && rejectedFiles.length > 0) {
      rejectedFiles.forEach(({ file, errors }) => {
        errors.forEach(error => {
          if (error.code === 'file-invalid-type') {
            toast.error(`${file.name} is not a PDF file. Please upload only PDF files.`, {
              duration: 4000,
              icon: '📄'
            });
          } else if (error.code === 'file-too-large') {
            toast.error(`${file.name} is too large. Maximum file size is 50MB.`, {
              duration: 4000,
              icon: '⚠️'
            });
          } else {
            toast.error(`${file.name} was rejected: ${error.message}`, {
              duration: 4000
            });
          }
        });
      });
      return;
    }

    // Handle accepted files
    if (acceptedFiles && acceptedFiles.length > 0) {
      setFiles(acceptedFiles);
      onFilesSelected(acceptedFiles);
    }
  }, [onFilesSelected]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    // Remove accept to show all files in file picker
    // Validation happens in the validator function
    maxSize: 50 * 1024 * 1024, // 50MB
    disabled,
    validator: (file) => {
      // Custom validator - files will be visible but validated on selection
      const isPDF = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
      
      if (!isPDF) {
        return {
          code: 'file-invalid-type',
          message: 'Only PDF files are allowed'
        };
      }
      
      if (file.size > 50 * 1024 * 1024) {
        return {
          code: 'file-too-large',
          message: 'File is larger than 50MB'
        };
      }
      
      return null;
    }
  });

  const removeFile = (index) => {
    const newFiles = files.filter((_, i) => i !== index);
    setFiles(newFiles);
    onFilesSelected(newFiles);
  };

  return (
    <div className="file-upload">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <svg
            className="upload-icon"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          {isDragActive ? (
            <p>Drop the PDF files here...</p>
          ) : (
            <>
              <p>Drag & drop PDF files here, or click to select</p>
              <p className="text-sm">Maximum file size: 50MB</p>
            </>
          )}
        </div>
      </div>

      {files.length > 0 && (
        <div className="file-list">
          <h3>Selected Files ({files.length})</h3>
          <ul>
            {files.map((file, index) => (
              <li key={index} className="file-item">
                <div className="file-info">
                  <svg
                    className="file-icon"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                  <div>
                    <p className="file-name">{file.name}</p>
                    <p className="file-size">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="remove-btn"
                  disabled={disabled}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
