import React from 'react';

const templates = [
  {
    id: 'template_1',
    name: 'Template 1 - Comprehensive Fund Data',
    description: 'Extract detailed fund information including performance metrics, investment data, and financial details'
  },
  {
    id: 'template_2',
    name: 'Template 2 - Key Metrics',
    description: 'Extract essential fund metrics and performance indicators'
  }
];

const TemplateSelector = ({ selectedTemplate, onTemplateSelect, disabled }) => {
  return (
    <div className="template-selector">
      <h3>Select Extraction Template</h3>
      <div className="template-options">
        {templates.map((template) => (
          <div
            key={template.id}
            className={`template-option ${selectedTemplate === template.id ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
            onClick={() => !disabled && onTemplateSelect(template.id)}
          >
            <div className="template-radio">
              <input
                type="radio"
                id={template.id}
                name="template"
                value={template.id}
                checked={selectedTemplate === template.id}
                onChange={() => onTemplateSelect(template.id)}
                disabled={disabled}
              />
            </div>
            <div className="template-info">
              <label htmlFor={template.id}>
                <h4>{template.name}</h4>
                <p>{template.description}</p>
              </label>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TemplateSelector;
