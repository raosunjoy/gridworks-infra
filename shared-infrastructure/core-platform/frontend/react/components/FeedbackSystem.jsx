/**
 * GridWorks Feedback Collection System
 * 
 * React component for collecting user feedback on charting platform features.
 * Provides contextual feedback forms, bug reporting, and analytics integration.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { ChartingAPI } from '../services/ChartingAPI';
import './FeedbackSystem.css';

const FeedbackSystem = ({
  isVisible,
  onClose,
  feature = 'general',
  context = {},
  authToken,
  userId,
  sessionId
}) => {
  // State management
  const [feedbackType, setFeedbackType] = useState('feature');
  const [rating, setRating] = useState(5);
  const [feedbackText, setFeedbackText] = useState('');
  const [bugDetails, setBugDetails] = useState({
    severity: 'medium',
    category: 'functionality',
    steps: '',
    expected: '',
    actual: ''
  });
  const [suggestions, setSuggestions] = useState('');
  const [usabilityScore, setUsabilityScore] = useState(8);
  const [performanceRating, setPerformanceRating] = useState(4);
  const [likelihoodToRecommend, setLikelihoodToRecommend] = useState(8);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  
  // API client
  const [api, setApi] = useState(null);
  
  useEffect(() => {
    if (authToken) {
      setApi(new ChartingAPI({
        baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
        authToken
      }));
    }
  }, [authToken]);
  
  // Reset form when feature changes
  useEffect(() => {
    if (isVisible) {
      resetForm();
    }
  }, [isVisible, feature]);
  
  const resetForm = () => {
    setCurrentStep(1);
    setFeedbackType('feature');
    setRating(5);
    setFeedbackText('');
    setBugDetails({
      severity: 'medium',
      category: 'functionality',
      steps: '',
      expected: '',
      actual: ''
    });
    setSuggestions('');
    setUsabilityScore(8);
    setPerformanceRating(4);
    setLikelihoodToRecommend(8);
    setSubmitSuccess(false);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!api) {
      alert('API not initialized');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const feedbackData = {
        feature,
        rating,
        feedback_text: feedbackText,
        bug_reports: feedbackType === 'bug' ? [{
          severity: bugDetails.severity,
          category: bugDetails.category,
          steps_to_reproduce: bugDetails.steps,
          expected_behavior: bugDetails.expected,
          actual_behavior: bugDetails.actual,
          context,
          user_agent: navigator.userAgent,
          timestamp: new Date().toISOString()
        }] : [],
        suggestions,
        usability_score: usabilityScore,
        performance_rating: performanceRating,
        likelihood_to_recommend: likelihoodToRecommend
      };
      
      // Submit feedback
      await api._request('POST', '/beta/feedback', feedbackData);
      
      // Track analytics
      await api._request('POST', '/beta/analytics', {
        event_name: 'feedback_submitted',
        event_data: {
          feature,
          feedback_type: feedbackType,
          rating,
          usability_score: usabilityScore,
          performance_rating: performanceRating
        },
        session_id: sessionId
      });
      
      setSubmitSuccess(true);
      setTimeout(() => {
        onClose();
      }, 2000);
      
    } catch (error) {
      console.error('Feedback submission error:', error);
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const nextStep = () => {
    setCurrentStep(prev => Math.min(prev + 1, 3));
  };
  
  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };
  
  const renderStarRating = (value, onChange, label) => (
    <div className="star-rating">
      <label>{label}</label>
      <div className="stars">
        {[1, 2, 3, 4, 5].map(star => (
          <button
            key={star}
            type="button"
            className={`star ${star <= value ? 'filled' : ''}`}
            onClick={() => onChange(star)}
          >
            ★
          </button>
        ))}
      </div>
      <span className="rating-text">
        {value === 1 ? 'Very Poor' :
         value === 2 ? 'Poor' :
         value === 3 ? 'Average' :
         value === 4 ? 'Good' : 'Excellent'}
      </span>
    </div>
  );
  
  const renderSliderRating = (value, onChange, label, min = 1, max = 10) => (
    <div className="slider-rating">
      <label>{label}</label>
      <div className="slider-container">
        <span>{min}</span>
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value))}
          className="slider"
        />
        <span>{max}</span>
      </div>
      <div className="slider-value">{value}</div>
    </div>
  );
  
  if (!isVisible) return null;
  
  if (submitSuccess) {
    return (
      <div className="feedback-overlay">
        <div className="feedback-modal success">
          <div className="success-icon">✓</div>
          <h3>Thank You!</h3>
          <p>Your feedback has been submitted successfully.</p>
          <p>We appreciate your input in making GridWorks better!</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="feedback-overlay">
      <div className="feedback-modal">
        <div className="feedback-header">
          <h3>Share Your Feedback</h3>
          <p>Help us improve the {feature.replace('_', ' ')} feature</p>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="feedback-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(currentStep / 3) * 100}%` }}
            ></div>
          </div>
          <span>Step {currentStep} of 3</span>
        </div>
        
        <form onSubmit={handleSubmit}>
          {/* Step 1: Feedback Type & Rating */}
          {currentStep === 1 && (
            <div className="feedback-step">
              <h4>What type of feedback would you like to share?</h4>
              
              <div className="feedback-type-selector">
                <label className={`type-option ${feedbackType === 'feature' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    value="feature"
                    checked={feedbackType === 'feature'}
                    onChange={(e) => setFeedbackType(e.target.value)}
                  />
                  <div className="option-content">
                    <span className="option-icon">💡</span>
                    <span>Feature Feedback</span>
                    <small>Share your thoughts on this feature</small>
                  </div>
                </label>
                
                <label className={`type-option ${feedbackType === 'bug' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    value="bug"
                    checked={feedbackType === 'bug'}
                    onChange={(e) => setFeedbackType(e.target.value)}
                  />
                  <div className="option-content">
                    <span className="option-icon">🐛</span>
                    <span>Bug Report</span>
                    <small>Report an issue or unexpected behavior</small>
                  </div>
                </label>
                
                <label className={`type-option ${feedbackType === 'suggestion' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    value="suggestion"
                    checked={feedbackType === 'suggestion'}
                    onChange={(e) => setFeedbackType(e.target.value)}
                  />
                  <div className="option-content">
                    <span className="option-icon">🚀</span>
                    <span>Improvement Suggestion</span>
                    <small>Suggest enhancements or new features</small>
                  </div>
                </label>
              </div>
              
              {feedbackType === 'feature' && (
                <div className="rating-section">
                  {renderStarRating(rating, setRating, "How would you rate this feature?")}
                </div>
              )}
              
              <div className="step-actions">
                <button type="button" onClick={nextStep} className="next-button">
                  Next Step →
                </button>
              </div>
            </div>
          )}
          
          {/* Step 2: Detailed Feedback */}
          {currentStep === 2 && (
            <div className="feedback-step">
              {feedbackType === 'bug' ? (
                <div className="bug-report-section">
                  <h4>Bug Report Details</h4>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>Severity</label>
                      <select
                        value={bugDetails.severity}
                        onChange={(e) => setBugDetails(prev => ({...prev, severity: e.target.value}))}
                      >
                        <option value="low">Low - Minor inconvenience</option>
                        <option value="medium">Medium - Affects functionality</option>
                        <option value="high">High - Blocks major features</option>
                        <option value="critical">Critical - App unusable</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label>Category</label>
                      <select
                        value={bugDetails.category}
                        onChange={(e) => setBugDetails(prev => ({...prev, category: e.target.value}))}
                      >
                        <option value="functionality">Functionality</option>
                        <option value="performance">Performance</option>
                        <option value="ui">User Interface</option>
                        <option value="data">Data/Chart Display</option>
                        <option value="voice">Voice Commands</option>
                        <option value="mobile">Mobile Experience</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label>Steps to Reproduce</label>
                    <textarea
                      value={bugDetails.steps}
                      onChange={(e) => setBugDetails(prev => ({...prev, steps: e.target.value}))}
                      placeholder="1. Click on...
2. Enter...
3. Notice that..."
                      rows={4}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Expected Behavior</label>
                    <textarea
                      value={bugDetails.expected}
                      onChange={(e) => setBugDetails(prev => ({...prev, expected: e.target.value}))}
                      placeholder="What did you expect to happen?"
                      rows={3}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Actual Behavior</label>
                    <textarea
                      value={bugDetails.actual}
                      onChange={(e) => setBugDetails(prev => ({...prev, actual: e.target.value}))}
                      placeholder="What actually happened?"
                      rows={3}
                    />
                  </div>
                </div>
              ) : (
                <div className="general-feedback-section">
                  <h4>Share Your Thoughts</h4>
                  
                  <div className="form-group">
                    <label>Your Feedback</label>
                    <textarea
                      value={feedbackText}
                      onChange={(e) => setFeedbackText(e.target.value)}
                      placeholder={feedbackType === 'suggestion' ? 
                        "What improvements would you like to see?" :
                        "Tell us about your experience with this feature..."
                      }
                      rows={6}
                      required
                    />
                  </div>
                  
                  {feedbackType === 'suggestion' && (
                    <div className="form-group">
                      <label>Specific Suggestions</label>
                      <textarea
                        value={suggestions}
                        onChange={(e) => setSuggestions(e.target.value)}
                        placeholder="Any specific features or improvements you'd like to see?"
                        rows={4}
                      />
                    </div>
                  )}
                </div>
              )}
              
              <div className="step-actions">
                <button type="button" onClick={prevStep} className="prev-button">
                  ← Previous
                </button>
                <button type="button" onClick={nextStep} className="next-button">
                  Next Step →
                </button>
              </div>
            </div>
          )}
          
          {/* Step 3: User Experience Ratings */}
          {currentStep === 3 && (
            <div className="feedback-step">
              <h4>Help Us Understand Your Experience</h4>
              
              <div className="ratings-section">
                {renderSliderRating(
                  usabilityScore,
                  setUsabilityScore,
                  "How easy was this feature to use?"
                )}
                
                {renderStarRating(
                  performanceRating,
                  setPerformanceRating,
                  "How would you rate the performance?"
                )}
                
                {renderSliderRating(
                  likelihoodToRecommend,
                  setLikelihoodToRecommend,
                  "How likely are you to recommend GridWorks to others?",
                  0,
                  10
                )}
              </div>
              
              <div className="step-actions">
                <button type="button" onClick={prevStep} className="prev-button">
                  ← Previous
                </button>
                <button 
                  type="submit" 
                  className="submit-button"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default FeedbackSystem;
export { FeedbackSystem };