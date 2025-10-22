import React, { useEffect, useState } from 'react';
import '../styles/ProcessingPage.css';

const ProcessingPage = ({ fileName, onProgressUpdate }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [dots, setDots] = useState('');

  const steps = [
    { icon: '📄', text: 'Reading PDF document', startProgress: 0, endProgress: 20 },
    { icon: '🔍', text: 'Analyzing content structure', startProgress: 20, endProgress: 35 },
    { icon: '🤖', text: 'AI processing with Gemini', startProgress: 35, endProgress: 70 },
    { icon: '📊', text: 'Structuring extracted data', startProgress: 70, endProgress: 85 },
    { icon: '📝', text: 'Generating Excel file', startProgress: 85, endProgress: 100 },
  ];

  // Animate dots
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => (prev.length >= 3 ? '' : prev + '.'));
    }, 500);

    return () => clearInterval(interval);
  }, []);

  // Smooth progress animation
  useEffect(() => {
    if (currentStep < steps.length) {
      const step = steps[currentStep];
      const duration = currentStep === 2 ? 3500 : 2000; // AI step takes longer
      const startProgress = step.startProgress;
      const endProgress = step.endProgress;
      const startTime = Date.now();

      const animateProgress = () => {
        const elapsed = Date.now() - startTime;
        const progressPercent = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuad = (t) => t * (2 - t);
        const easedProgress = easeOutQuad(progressPercent);
        
        const currentProgress = startProgress + (endProgress - startProgress) * easedProgress;
        setProgress(Math.round(currentProgress));

        if (progressPercent < 1) {
          requestAnimationFrame(animateProgress);
        } else if (currentStep < steps.length - 1) {
          // Move to next step
          setTimeout(() => setCurrentStep(prev => prev + 1), 300);
        } else {
          // Notify parent that processing is complete
          if (onProgressUpdate) {
            onProgressUpdate(100);
          }
        }
      };

      requestAnimationFrame(animateProgress);
    }
  }, [currentStep]);

  return (
    <div className="processing-page">
      <div className="processing-container">
        {/* Header */}
        <div className="processing-header">
          <div className="file-icon">📄</div>
          <h2>Processing Your Document</h2>
          <p className="file-name">{fileName}</p>
        </div>

        {/* Animated Loader */}
        <div className="loader-container">
          <div className="circular-loader">
            <svg className="circular-svg" viewBox="0 0 100 100">
              <defs>
                <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#667eea" />
                  <stop offset="100%" stopColor="#764ba2" />
                </linearGradient>
              </defs>
              <circle
                className="circular-bg"
                cx="50"
                cy="50"
                r="45"
                fill="none"
                strokeWidth="8"
              />
              <circle
                className="circular-progress"
                cx="50"
                cy="50"
                r="45"
                fill="none"
                strokeWidth="8"
                strokeDasharray={`${progress * 2.827}, 282.7`}
                style={{ transition: 'stroke-dasharray 0.3s ease' }}
              />
            </svg>
            <div className="loader-percentage">
              {progress}%
              {progress === 100 && <span className="completion-check">✓</span>}
            </div>
          </div>
        </div>

        {/* Steps */}
        <div className="processing-steps">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`step ${index === currentStep ? 'active' : ''} ${
                index < currentStep ? 'completed' : ''
              }`}
            >
              <div className="step-icon">{step.icon}</div>
              <div className="step-text">
                {step.text}
                {index === currentStep && <span className="dots">{dots}</span>}
              </div>
              {index < currentStep && (
                <div className="step-check">✓</div>
              )}
            </div>
          ))}
        </div>

        {/* Progress Bar */}
        <div className="progress-bar-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="progress-text">
            Processing... Please wait
          </div>
        </div>

        {/* Info Message */}
        <div className="processing-info">
          <div className="info-icon">ℹ️</div>
          <p>
            This may take a minute. We're using advanced AI to extract
            structured data from your PDF.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProcessingPage;
