import { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const TemplateSelector = ({ selectedTemplate, onTemplateSelect, disabled }) => {
  const [templates, setTemplates] = useState([
    {
      template_id: 'portfolio_summary_template',
      name: 'Portfolio Summary (Field | Value Format)',
      description: 'Extract fund-level data in vertical Field | Value format with ALL portfolio companies. Includes separate sheets for each company.',
      output_format: 'vertical'
    },
    {
      template_id: 'template_1',
      name: 'Comprehensive Fund Data (Column Format)',
      description: 'Extract detailed fund information in column format including performance metrics, investment data, and ALL companies.',
      output_format: 'horizontal'
    },
    {
      template_id: 'template_2',
      name: 'Key Metrics (Column Format)',
      description: 'Extract essential fund metrics and performance indicators in column format with ALL portfolio companies.',
      output_format: 'horizontal'
    }
  ]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch available templates from API
    const fetchTemplates = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/templates`);
        if (response.ok) {
          const data = await response.json();
          if (data.templates && data.templates.length > 0) {
            // Map API templates to component format
            const apiTemplates = data.templates.map(t => ({
              template_id: t.template_id || t.id,
              name: t.name,
              description: t.description || 'No description available',
              output_format: t.output_format || 'vertical'
            }));
            setTemplates(apiTemplates);
          }
        }
      } catch (error) {
        console.warn('Could not fetch templates from API, using defaults:', error);
        // Keep default templates if API fetch fails
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  return (
    <div className="template-selector">
      <h3>
        Select Extraction Template
        {loading && <span className="loading-indicator"> (Loading...)</span>}
      </h3>
      <div className="template-description">
        <p>
          <strong>All templates now extract ALL portfolio companies</strong> (not just the first one).
          Choose the format that best matches your needs:
        </p>
      </div>
      <div className="template-options">
        {templates.map((template) => (
          <div
            key={template.template_id}
            className={`template-option ${selectedTemplate === template.template_id ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
            onClick={() => !disabled && onTemplateSelect(template.template_id)}
          >
            <div className="template-radio">
              <input
                type="radio"
                id={template.template_id}
                name="template"
                value={template.template_id}
                checked={selectedTemplate === template.template_id}
                onChange={() => onTemplateSelect(template.template_id)}
                disabled={disabled}
              />
            </div>
            <div className="template-info">
              <label htmlFor={template.template_id}>
                <h4>
                  {template.name}
                  {template.output_format && (
                    <span className="template-format-badge">
                      {template.output_format === 'vertical' ? '📋 Vertical' : '📊 Horizontal'}
                    </span>
                  )}
                </h4>
                <p>{template.description}</p>
              </label>
            </div>
          </div>
        ))}
      </div>
      <div className="template-note">
        <p className="info-text">
          ℹ️ <strong>Improved Extraction:</strong> All templates use the enhanced 3-step extraction process
          to find and extract data for ALL portfolio companies in the PDF.
        </p>
      </div>
    </div>
  );
};

export default TemplateSelector;
