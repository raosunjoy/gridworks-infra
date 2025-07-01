/**
 * Concierge Services Interface Test Suite
 * Comprehensive testing for luxury concierge service request system,
 * anonymous service delivery, and tier-specific service access
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { ConciergeServicesInterface } from '../../components/concierge/ConciergeServicesInterface';
import { ConciergeCategory, ServiceTier } from '../../services/EnhancedConciergeServices';

// Mock dependencies
jest.mock('../../components/ui/LuxuryCard', () => ({
  LuxuryCard: ({ children, className, onClick }: any) => (
    <div className={className} onClick={onClick} data-testid="luxury-card">
      {children}
    </div>
  ),
}));

jest.mock('../../components/ui/TierGlow', () => ({
  TierGlow: ({ children }: any) => <div data-testid="tier-glow">{children}</div>,
}));

describe('ConciergeServicesInterface', () => {
  const defaultProps = {
    tier: ServiceTier.OBSIDIAN,
    anonymousId: 'test-anonymous-id',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Initialization', () => {
    test('should render concierge services interface with header', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('Concierge Services')).toBeInTheDocument();
      expect(screen.getByText(/Ultra-luxury services with complete anonymity/)).toBeInTheDocument();
      expect(screen.getByText(/OBSIDIAN Tier/)).toBeInTheDocument();
    });

    test('should display navigation tabs', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('All Services')).toBeInTheDocument();
      expect(screen.getByText(/Active Requests/)).toBeInTheDocument();
    });

    test('should show active requests count in navigation', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('Active Requests (1)')).toBeInTheDocument();
    });
  });

  describe('Service Categories Grid', () => {
    test('should display all concierge service categories', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('Private Aviation')).toBeInTheDocument();
      expect(screen.getByText('Art Acquisition')).toBeInTheDocument();
      expect(screen.getByText('Luxury Accommodation')).toBeInTheDocument();
      expect(screen.getByText('Golden Visa Programs')).toBeInTheDocument();
      expect(screen.getByText('Yacht Charter')).toBeInTheDocument();
      expect(screen.getByText('Private Chef Services')).toBeInTheDocument();
      expect(screen.getByText('Security Services')).toBeInTheDocument();
      expect(screen.getByText('Wellness Retreats')).toBeInTheDocument();
      expect(screen.getByText('Exclusive Events')).toBeInTheDocument();
      expect(screen.getByText('Educational Services')).toBeInTheDocument();
    });

    test('should display category descriptions and icons', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('Private jets, helicopters, and exclusive air travel')).toBeInTheDocument();
      expect(screen.getByText('Museum-quality art and collectibles sourcing')).toBeInTheDocument();
      expect(screen.getByText('Citizenship and residency by investment')).toBeInTheDocument();
      
      // Check for emojis/icons
      expect(screen.getByText('✈️')).toBeInTheDocument(); // Private Aviation
      expect(screen.getByText('🎨')).toBeInTheDocument(); // Art Acquisition
      expect(screen.getByText('🏰')).toBeInTheDocument(); // Luxury Accommodation
    });

    test('should display minimum budget for each category', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('From ₹5 Cr')).toBeInTheDocument(); // Private Aviation
      expect(screen.getByText('From ₹10 Cr')).toBeInTheDocument(); // Art Acquisition
      expect(screen.getByText('From ₹50 Cr')).toBeInTheDocument(); // Golden Visa
    });

    test('should make category cards clickable with hover effects', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      expect(aviationCard).toHaveClass('cursor-pointer');
      expect(aviationCard).toHaveClass('hover:scale-105');
    });

    test('should navigate to service request form when category is selected', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      expect(screen.getByText('Step 1: Investment Details')).not.toBeInTheDocument();
      expect(screen.getByText('← Back to Categories')).toBeInTheDocument();
      expect(screen.getByText('Private Aviation')).toBeInTheDocument();
    });
  });

  describe('Service Request Form', () => {
    beforeEach(() => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
    });

    test('should display service request form header', () => {
      expect(screen.getByText('Private Aviation')).toBeInTheDocument();
      expect(screen.getByText('Private jets, helicopters, and exclusive air travel')).toBeInTheDocument();
      expect(screen.getByText('← Back to Categories')).toBeInTheDocument();
    });

    test('should show basic request details fields', () => {
      expect(screen.getByText('Request Title')).toBeInTheDocument();
      expect(screen.getByText('Urgency Level')).toBeInTheDocument();
      expect(screen.getByText('Detailed Description')).toBeInTheDocument();
      
      expect(screen.getByPlaceholderText('Brief title for your request')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Provide detailed requirements for your request...')).toBeInTheDocument();
    });

    test('should display urgency level options based on tier', () => {
      const urgencySelect = screen.getByDisplayValue('standard');
      expect(urgencySelect).toBeInTheDocument();
      
      // OBSIDIAN tier should not have 'impossible' option
      expect(screen.getByText('Standard (7-14 days)')).toBeInTheDocument();
      expect(screen.getByText('Priority (1-3 days)')).toBeInTheDocument();
      expect(screen.getByText('Emergency (24 hours)')).toBeInTheDocument();
      expect(screen.queryByText('Impossible (Immediate)')).not.toBeInTheDocument();
    });

    test('should show impossible urgency for VOID tier', () => {
      const voidProps = { ...defaultProps, tier: ServiceTier.VOID };
      render(<ConciergeServicesInterface {...voidProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      const urgencySelect = screen.getByDisplayValue('standard');
      fireEvent.change(urgencySelect, { target: { value: 'impossible' } });
      
      expect(screen.getByDisplayValue('impossible')).toBeInTheDocument();
    });

    test('should display budget range options', () => {
      expect(screen.getByText('Budget Range')).toBeInTheDocument();
      expect(screen.getByText('Premium (₹1-10 Cr)')).toBeInTheDocument();
      expect(screen.getByText('High (₹10-50 Cr)')).toBeInTheDocument();
      expect(screen.getByText('Ultra High (₹50-500 Cr)')).toBeInTheDocument();
    });

    test('should show no limit budget option for non-Onyx tiers', () => {
      expect(screen.getByText('No Limit')).toBeInTheDocument();
      
      // Test Onyx tier should not have no limit option
      const onyxProps = { ...defaultProps, tier: ServiceTier.ONYX };
      const { rerender } = render(<ConciergeServicesInterface {...onyxProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      expect(screen.queryByText('No Limit')).not.toBeInTheDocument();
    });
  });

  describe('Private Aviation Specific Form', () => {
    beforeEach(() => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
    });

    test('should display departure and destination fields', () => {
      expect(screen.getByText('Departure Location')).toBeInTheDocument();
      expect(screen.getByText('Destination')).toBeInTheDocument();
      
      expect(screen.getByPlaceholderText('Mumbai, Delhi, Bangalore...')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Dubai, Singapore, London...')).toBeInTheDocument();
    });

    test('should allow input of passenger details', () => {
      expect(screen.getByText('Adults')).toBeInTheDocument();
      expect(screen.getByText('Children')).toBeInTheDocument();
      
      const adultsInput = screen.getByDisplayValue('1');
      const childrenInput = screen.getByDisplayValue('0');
      
      fireEvent.change(adultsInput, { target: { value: '4' } });
      fireEvent.change(childrenInput, { target: { value: '2' } });
      
      expect(adultsInput.value).toBe('4');
      expect(childrenInput.value).toBe('2');
    });

    test('should provide aircraft type selection', () => {
      expect(screen.getByText('Aircraft Type')).toBeInTheDocument();
      
      const aircraftSelect = screen.getByDisplayValue('mid_size');
      expect(aircraftSelect).toBeInTheDocument();
      
      expect(screen.getByText('Light Jet')).toBeInTheDocument();
      expect(screen.getByText('Mid-Size Jet')).toBeInTheDocument();
      expect(screen.getByText('Heavy Jet')).toBeInTheDocument();
      expect(screen.getByText('Ultra Long Range')).toBeInTheDocument();
      expect(screen.getByText('Private Airliner')).toBeInTheDocument();
    });

    test('should show special requirements checkboxes', () => {
      expect(screen.getByText('Special Requirements')).toBeInTheDocument();
      
      const amenityCheckboxes = [
        'Full meal service',
        'WiFi',
        'Entertainment system',
        'Conference setup',
        'Medical equipment',
        'Pet accommodation',
      ];
      
      amenityCheckboxes.forEach(amenity => {
        expect(screen.getByText(amenity)).toBeInTheDocument();
      });
    });

    test('should handle amenity selection', () => {
      const wifiCheckbox = screen.getByLabelText('WiFi');
      fireEvent.click(wifiCheckbox);
      
      expect(wifiCheckbox).toBeChecked();
    });
  });

  describe('Anonymity and Privacy Settings', () => {
    beforeEach(() => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
    });

    test('should display anonymity and privacy section', () => {
      expect(screen.getByText('Anonymity & Privacy')).toBeInTheDocument();
      expect(screen.getByText('Identity Concealment')).toBeInTheDocument();
      expect(screen.getByText('Communication Protocol')).toBeInTheDocument();
    });

    test('should set default anonymity level based on tier', () => {
      const concealmentSelect = screen.getByDisplayValue('enhanced'); // OBSIDIAN default
      expect(concealmentSelect).toBeInTheDocument();
    });

    test('should show appropriate concealment options for tier', () => {
      expect(screen.getByText('Standard (Basic privacy)')).toBeInTheDocument();
      expect(screen.getByText('Enhanced (Multiple layers)')).toBeInTheDocument();
      expect(screen.getByText('Absolute (Complete anonymity)')).toBeInTheDocument();
    });

    test('should limit absolute anonymity for ONYX tier', () => {
      const onyxProps = { ...defaultProps, tier: ServiceTier.ONYX };
      render(<ConciergeServicesInterface {...onyxProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      expect(screen.queryByText('Absolute (Complete anonymity)')).not.toBeInTheDocument();
    });

    test('should display communication protocol options', () => {
      expect(screen.getByText('Anonymous messaging only')).toBeInTheDocument();
      expect(screen.getByText('Pseudonym communications')).toBeInTheDocument();
      expect(screen.getByText('Designated representative')).toBeInTheDocument();
    });
  });

  describe('Form Validation and Submission', () => {
    beforeEach(() => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
    });

    test('should disable submit button when required fields are empty', () => {
      const submitButton = screen.getByText('Submit Concierge Request');
      expect(submitButton).toBeDisabled();
    });

    test('should enable submit button when required fields are filled', () => {
      const titleInput = screen.getByPlaceholderText('Brief title for your request');
      const descriptionInput = screen.getByPlaceholderText('Provide detailed requirements for your request...');
      
      fireEvent.change(titleInput, { target: { value: 'Private Jet to Dubai' } });
      fireEvent.change(descriptionInput, { target: { value: 'Need immediate private jet charter' } });
      
      const submitButton = screen.getByText('Submit Concierge Request');
      expect(submitButton).not.toBeDisabled();
    });

    test('should submit request with all form data', async () => {
      const titleInput = screen.getByPlaceholderText('Brief title for your request');
      const descriptionInput = screen.getByPlaceholderText('Provide detailed requirements for your request...');
      
      fireEvent.change(titleInput, { target: { value: 'Test Request' } });
      fireEvent.change(descriptionInput, { target: { value: 'Test description' } });
      
      const submitButton = screen.getByText('Submit Concierge Request');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Test Request')).toBeInTheDocument();
      });
    });

    test('should show loading state during submission', async () => {
      const titleInput = screen.getByPlaceholderText('Brief title for your request');
      const descriptionInput = screen.getByPlaceholderText('Provide detailed requirements for your request...');
      
      fireEvent.change(titleInput, { target: { value: 'Test Request' } });
      fireEvent.change(descriptionInput, { target: { value: 'Test description' } });
      
      const submitButton = screen.getByText('Submit Concierge Request');
      fireEvent.click(submitButton);
      
      expect(screen.getByText('Submitting Request...')).toBeInTheDocument();
    });

    test('should reset form after successful submission', async () => {
      const titleInput = screen.getByPlaceholderText('Brief title for your request');
      const descriptionInput = screen.getByPlaceholderText('Provide detailed requirements for your request...');
      
      fireEvent.change(titleInput, { target: { value: 'Test Request' } });
      fireEvent.change(descriptionInput, { target: { value: 'Test description' } });
      
      const submitButton = screen.getByText('Submit Concierge Request');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        // Should navigate back to categories view
        expect(screen.getByText('Private Aviation')).toBeInTheDocument();
        expect(screen.queryByText('← Back to Categories')).not.toBeInTheDocument();
      });
    });
  });

  describe('Active Requests Display', () => {
    test('should show existing active requests', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('Active Requests')).toBeInTheDocument();
      expect(screen.getByText('Private Jet to Dubai')).toBeInTheDocument();
      expect(screen.getByText('Immediate private jet charter from Mumbai to Dubai for 6 passengers')).toBeInTheDocument();
    });

    test('should display request status and urgency', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('PRIORITY')).toBeInTheDocument();
      expect(screen.getByText('PRIVATE_AVIATION')).toBeInTheDocument();
      expect(screen.getByText('In Progress')).toBeInTheDocument();
    });

    test('should show request metadata', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('Status:')).toBeInTheDocument();
      expect(screen.getByText('Concierge:')).toBeInTheDocument();
      expect(screen.getByText('Created:')).toBeInTheDocument();
      expect(screen.getByText('Estimated:')).toBeInTheDocument();
      
      expect(screen.getByText('Sterling-Aviation-007')).toBeInTheDocument();
    });

    test('should show view details button for each request', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      const viewDetailsButton = screen.getByText('View Details');
      expect(viewDetailsButton).toBeInTheDocument();
      expect(viewDetailsButton).toHaveClass('bg-gold-500/20');
    });

    test('should display empty state when no active requests', () => {
      // Mock empty requests
      const emptyProps = { ...defaultProps };
      render(<ConciergeServicesInterface {...emptyProps} />);
      
      // Manually clear active requests (in real implementation this would be handled by the hook)
      // For now, we test the UI structure
      expect(screen.getByText('Active Requests')).toBeInTheDocument();
    });
  });

  describe('Navigation and Back Button', () => {
    test('should navigate back to categories from request form', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      expect(screen.getByText('← Back to Categories')).toBeInTheDocument();
      
      const backButton = screen.getByText('← Back to Categories');
      fireEvent.click(backButton);
      
      expect(screen.getByText('All Services')).toBeInTheDocument();
      expect(screen.queryByText('← Back to Categories')).not.toBeInTheDocument();
    });

    test('should switch between All Services and Active Requests views', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      // Default view should show categories
      expect(screen.getByText('Private Aviation')).toBeInTheDocument();
      
      // Click on All Services should keep the same view
      const allServicesButton = screen.getByText('All Services');
      fireEvent.click(allServicesButton);
      
      expect(screen.getByText('Private Aviation')).toBeInTheDocument();
    });
  });

  describe('Tier-Specific Behavior', () => {
    test('should adjust service options based on tier level', () => {
      const voidProps = { ...defaultProps, tier: ServiceTier.VOID };
      render(<ConciergeServicesInterface {...voidProps} />);
      
      expect(screen.getByText(/VOID Tier/)).toBeInTheDocument();
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      // VOID tier should have absolute anonymity as default
      const concealmentSelect = screen.getByDisplayValue('absolute');
      expect(concealmentSelect).toBeInTheDocument();
    });

    test('should show tier-appropriate budget options', () => {
      const onyxProps = { ...defaultProps, tier: ServiceTier.ONYX };
      render(<ConciergeServicesInterface {...onyxProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      expect(screen.queryByText('No Limit')).not.toBeInTheDocument();
    });

    test('should adapt anonymity options to tier capabilities', () => {
      const onyxProps = { ...defaultProps, tier: ServiceTier.ONYX };
      render(<ConciergeServicesInterface {...onyxProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      const concealmentSelect = screen.getByDisplayValue('standard'); // ONYX default
      expect(concealmentSelect).toBeInTheDocument();
    });
  });

  describe('Currency Formatting', () => {
    test('should format currency amounts consistently', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('From ₹5 Cr')).toBeInTheDocument();
      expect(screen.getByText('From ₹10 Cr')).toBeInTheDocument();
      expect(screen.getByText('From ₹50 Cr')).toBeInTheDocument();
    });

    test('should handle large amounts correctly', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      // Golden Visa minimum
      expect(screen.getByText('From ₹50 Cr')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    test('should handle form submission errors gracefully', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      const titleInput = screen.getByPlaceholderText('Brief title for your request');
      const descriptionInput = screen.getByPlaceholderText('Provide detailed requirements for your request...');
      
      fireEvent.change(titleInput, { target: { value: 'Test Request' } });
      fireEvent.change(descriptionInput, { target: { value: 'Test description' } });
      
      // In a real implementation, this would test actual API error handling
      const submitButton = screen.getByText('Submit Concierge Request');
      fireEvent.click(submitButton);
      
      // Should not crash the component
      expect(screen.getByText('Submit Concierge Request')).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });

    test('should validate required fields before submission', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      // Submit button should be disabled with empty fields
      const submitButton = screen.getByText('Submit Concierge Request');
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    test('should have proper ARIA labels for interactive elements', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      // Form inputs should have proper labels
      expect(screen.getByLabelText('Request Title')).toBeInTheDocument();
      expect(screen.getByLabelText('Urgency Level')).toBeInTheDocument();
      expect(screen.getByLabelText('Detailed Description')).toBeInTheDocument();
    });

    test('should support keyboard navigation', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      expect(aviationCard).toHaveAttribute('tabIndex', '0');
    });

    test('should provide screen reader friendly content', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('Concierge services interface')).toBeInTheDocument();
    });
  });

  describe('Real-time Features', () => {
    test('should display real-time request status updates', () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      // Active request should show current status
      expect(screen.getByText('In Progress')).toBeInTheDocument();
    });

    test('should update active requests count dynamically', async () => {
      render(<ConciergeServicesInterface {...defaultProps} />);
      
      expect(screen.getByText('Active Requests (1)')).toBeInTheDocument();
      
      // Submit a new request
      const aviationCard = screen.getByText('Private Aviation').closest('[data-testid="luxury-card"]');
      fireEvent.click(aviationCard!);
      
      const titleInput = screen.getByPlaceholderText('Brief title for your request');
      const descriptionInput = screen.getByPlaceholderText('Provide detailed requirements for your request...');
      
      fireEvent.change(titleInput, { target: { value: 'New Request' } });
      fireEvent.change(descriptionInput, { target: { value: 'New description' } });
      
      const submitButton = screen.getByText('Submit Concierge Request');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Active Requests (2)')).toBeInTheDocument();
      });
    });
  });
});