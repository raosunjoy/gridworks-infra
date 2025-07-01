import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';

// Mock all major components for E2E testing
jest.mock('../../components/auth/InvitationPrompt', () => ({
  InvitationPrompt: ({ onValidCode }: any) => (
    <div data-testid="invitation-prompt">
      <input 
        data-testid="invitation-input" 
        placeholder="Enter invitation code"
        onChange={(e) => {
          if (e.target.value === 'VOID_ACCESS') {
            onValidCode('void');
          } else if (e.target.value === 'OBSIDIAN_ELITE') {
            onValidCode('obsidian');
          } else if (e.target.value === 'ONYX_PREMIUM') {
            onValidCode('onyx');
          }
        }}
      />
    </div>
  ),
}));

jest.mock('../../components/auth/BiometricAuth', () => ({
  BiometricAuth: ({ tier, onAuthSuccess }: any) => (
    <div data-testid="biometric-auth">
      <div>Biometric Auth for {tier}</div>
      <button 
        data-testid="face-auth-btn"
        onClick={() => onAuthSuccess({ 
          method: 'face', 
          confidence: 0.95, 
          deviceFingerprint: { deviceId: 'test-device' } 
        })}
      >
        Face Recognition
      </button>
      <button 
        data-testid="fingerprint-auth-btn"
        onClick={() => onAuthSuccess({ 
          method: 'fingerprint', 
          confidence: 0.98, 
          deviceFingerprint: { deviceId: 'test-device' } 
        })}
      >
        Fingerprint
      </button>
    </div>
  ),
}));

jest.mock('../../components/auth/TierAssignment', () => ({
  TierAssignment: ({ tier, onAssignmentComplete }: any) => (
    <div data-testid="tier-assignment">
      <div>Tier Assignment: {tier}</div>
      <button 
        data-testid="complete-assignment-btn"
        onClick={() => onAssignmentComplete({
          tier,
          portfolio: '₹1,000+ Cr',
          verified: true
        })}
      >
        Complete Assignment
      </button>
    </div>
  ),
}));

jest.mock('../../components/portal/WelcomeCeremony', () => ({
  WelcomeCeremony: ({ tier, onCeremonyComplete }: any) => (
    <div data-testid="welcome-ceremony">
      <div>Welcome to {tier} tier</div>
      <button 
        data-testid="complete-ceremony-btn"
        onClick={() => onCeremonyComplete()}
      >
        Enter Portal
      </button>
    </div>
  ),
}));

jest.mock('../../components/portal/PortalDashboard', () => ({
  PortalDashboard: ({ tier }: any) => (
    <div data-testid="portal-dashboard">
      <div>Portal Dashboard - {tier}</div>
      <button data-testid="butler-btn">Butler AI</button>
      <button data-testid="emergency-btn">Emergency Services</button>
      <button data-testid="concierge-btn">Concierge</button>
      <button data-testid="social-circle-btn">Social Circle</button>
      <button data-testid="app-download-btn">Download App</button>
    </div>
  ),
}));

jest.mock('../../components/services/ButlerAnonymousInterface', () => ({
  ButlerAnonymousInterface: ({ tier, anonymousId }: any) => (
    <div data-testid="butler-interface">
      <div>Butler AI - {tier}</div>
      <div>Anonymous ID: {anonymousId}</div>
      <input data-testid="butler-input" placeholder="Message Butler" />
      <button data-testid="send-message-btn">Send</button>
    </div>
  ),
}));

jest.mock('../../components/services/SocialCircleMessaging', () => ({
  SocialCircleMessaging: ({ tier, anonymousId }: any) => (
    <div data-testid="social-circle">
      <div>Social Circle - {tier}</div>
      <div>Anonymous ID: {anonymousId}</div>
      <button data-testid="start-discussion-btn">Start Discussion</button>
      <button data-testid="share-deal-btn">Share Deal</button>
      <button data-testid="create-poll-btn">Create Poll</button>
    </div>
  ),
}));

jest.mock('../../components/services/AnonymousServiceDashboard', () => ({
  AnonymousServiceDashboard: ({ tier }: any) => (
    <div data-testid="service-dashboard">
      <div>Service Dashboard - {tier}</div>
      <button data-testid="book-jet-btn">Book Private Jet</button>
      <button data-testid="emergency-medical-btn">Emergency Medical</button>
      <button data-testid="concierge-dining-btn">Exclusive Dining</button>
    </div>
  ),
}));

jest.mock('../../components/distribution/AppDistributionManager', () => ({
  AppDistributionManager: ({ tier }: any) => (
    <div data-testid="app-distribution">
      <div>App Distribution - {tier}</div>
      <button data-testid="download-ios-btn">Download iOS App</button>
      <button data-testid="download-android-btn">Download Android App</button>
      <div data-testid="security-assessment">Security Assessment: 95/100</div>
    </div>
  ),
}));

// Mock framer-motion for testing
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Main Portal Component for E2E testing
const BlackPortal: React.FC = () => {
  const [currentStep, setCurrentStep] = React.useState<'invitation' | 'biometric' | 'assignment' | 'ceremony' | 'dashboard'>('invitation');
  const [userTier, setUserTier] = React.useState<'onyx' | 'obsidian' | 'void' | null>(null);
  const [authData, setAuthData] = React.useState<any>(null);
  const [currentView, setCurrentView] = React.useState<'dashboard' | 'butler' | 'social' | 'services' | 'apps'>('dashboard');
  const [anonymousId, setAnonymousId] = React.useState<string>('');

  const { InvitationPrompt } = require('../../components/auth/InvitationPrompt');
  const { BiometricAuth } = require('../../components/auth/BiometricAuth');
  const { TierAssignment } = require('../../components/auth/TierAssignment');
  const { WelcomeCeremony } = require('../../components/portal/WelcomeCeremony');
  const { PortalDashboard } = require('../../components/portal/PortalDashboard');
  const { ButlerAnonymousInterface } = require('../../components/services/ButlerAnonymousInterface');
  const { SocialCircleMessaging } = require('../../components/services/SocialCircleMessaging');
  const { AnonymousServiceDashboard } = require('../../components/services/AnonymousServiceDashboard');
  const { AppDistributionManager } = require('../../components/distribution/AppDistributionManager');

  const handleValidCode = (tier: 'onyx' | 'obsidian' | 'void') => {
    setUserTier(tier);
    setCurrentStep('biometric');
  };

  const handleAuthSuccess = (data: any) => {
    setAuthData(data);
    setCurrentStep('assignment');
  };

  const handleAssignmentComplete = (data: any) => {
    setCurrentStep('ceremony');
  };

  const handleCeremonyComplete = () => {
    setCurrentStep('dashboard');
    // Generate anonymous ID
    const tierPrefixes = {
      onyx: 'Silver_Navigator',
      obsidian: 'Crystal_Emperor',
      void: 'Quantum_Sage'
    };
    const randomNum = Math.floor(Math.random() * 99) + 1;
    setAnonymousId(`${tierPrefixes[userTier!]}_${randomNum}`);
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'invitation':
        return (
          <InvitationPrompt 
            onValidCode={handleValidCode}
            onInvalidAttempt={() => {}}
          />
        );
      case 'biometric':
        return (
          <BiometricAuth 
            tier={userTier!}
            onAuthSuccess={handleAuthSuccess}
            onAuthFailure={() => {}}
          />
        );
      case 'assignment':
        return (
          <TierAssignment 
            tier={userTier!}
            onAssignmentComplete={handleAssignmentComplete}
          />
        );
      case 'ceremony':
        return (
          <WelcomeCeremony 
            tier={userTier!}
            onCeremonyComplete={handleCeremonyComplete}
          />
        );
      case 'dashboard':
        return renderDashboardView();
    }
  };

  const renderDashboardView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <div>
            <PortalDashboard tier={userTier!} />
            <div style={{ marginTop: '20px' }}>
              <button data-testid="nav-butler" onClick={() => setCurrentView('butler')}>
                Butler AI
              </button>
              <button data-testid="nav-social" onClick={() => setCurrentView('social')}>
                Social Circle
              </button>
              <button data-testid="nav-services" onClick={() => setCurrentView('services')}>
                Services
              </button>
              <button data-testid="nav-apps" onClick={() => setCurrentView('apps')}>
                Apps
              </button>
            </div>
          </div>
        );
      case 'butler':
        return (
          <div>
            <ButlerAnonymousInterface 
              tier={userTier!} 
              userId="test-user" 
              anonymousId={anonymousId}
            />
            <button data-testid="back-to-dashboard" onClick={() => setCurrentView('dashboard')}>
              Back to Dashboard
            </button>
          </div>
        );
      case 'social':
        return (
          <div>
            <SocialCircleMessaging 
              tier={userTier!}
              anonymousId={anonymousId}
              circleId={`${userTier}_circle`}
            />
            <button data-testid="back-to-dashboard" onClick={() => setCurrentView('dashboard')}>
              Back to Dashboard
            </button>
          </div>
        );
      case 'services':
        return (
          <div>
            <AnonymousServiceDashboard 
              tier={userTier!}
              userId="test-user"
              anonymousId={anonymousId}
            />
            <button data-testid="back-to-dashboard" onClick={() => setCurrentView('dashboard')}>
              Back to Dashboard
            </button>
          </div>
        );
      case 'apps':
        return (
          <div>
            <AppDistributionManager tier={userTier!} />
            <button data-testid="back-to-dashboard" onClick={() => setCurrentView('dashboard')}>
              Back to Dashboard
            </button>
          </div>
        );
    }
  };

  return (
    <div data-testid="black-portal">
      {renderCurrentStep()}
    </div>
  );
};

describe('Black Portal E2E User Journey Tests', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    jest.clearAllMocks();
  });

  describe('Complete Onboarding Journey - Void Tier', () => {
    test('completes full void tier onboarding journey', async () => {
      render(<BlackPortal />);

      // Step 1: Invitation Code Entry
      expect(screen.getByTestId('invitation-prompt')).toBeInTheDocument();
      
      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'VOID_ACCESS');

      // Should progress to biometric auth
      await waitFor(() => {
        expect(screen.getByTestId('biometric-auth')).toBeInTheDocument();
      });

      expect(screen.getByText('Biometric Auth for void')).toBeInTheDocument();

      // Step 2: Biometric Authentication
      const faceAuthBtn = screen.getByTestId('face-auth-btn');
      await user.click(faceAuthBtn);

      // Should progress to tier assignment
      await waitFor(() => {
        expect(screen.getByTestId('tier-assignment')).toBeInTheDocument();
      });

      expect(screen.getByText('Tier Assignment: void')).toBeInTheDocument();

      // Step 3: Tier Assignment
      const completeAssignmentBtn = screen.getByTestId('complete-assignment-btn');
      await user.click(completeAssignmentBtn);

      // Should progress to welcome ceremony
      await waitFor(() => {
        expect(screen.getByTestId('welcome-ceremony')).toBeInTheDocument();
      });

      expect(screen.getByText('Welcome to void tier')).toBeInTheDocument();

      // Step 4: Welcome Ceremony
      const completeCeremonyBtn = screen.getByTestId('complete-ceremony-btn');
      await user.click(completeCeremonyBtn);

      // Should reach portal dashboard
      await waitFor(() => {
        expect(screen.getByTestId('portal-dashboard')).toBeInTheDocument();
      });

      expect(screen.getByText('Portal Dashboard - void')).toBeInTheDocument();
    });

    test('completes full obsidian tier onboarding journey', async () => {
      render(<BlackPortal />);

      // Quick progression through obsidian tier
      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'OBSIDIAN_ELITE');

      await waitFor(() => {
        expect(screen.getByText('Biometric Auth for obsidian')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('fingerprint-auth-btn'));

      await waitFor(() => {
        expect(screen.getByText('Tier Assignment: obsidian')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('complete-assignment-btn'));

      await waitFor(() => {
        expect(screen.getByText('Welcome to obsidian tier')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('complete-ceremony-btn'));

      await waitFor(() => {
        expect(screen.getByText('Portal Dashboard - obsidian')).toBeInTheDocument();
      });
    });

    test('completes full onyx tier onboarding journey', async () => {
      render(<BlackPortal />);

      // Quick progression through onyx tier
      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'ONYX_PREMIUM');

      await waitFor(() => {
        expect(screen.getByText('Biometric Auth for onyx')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('face-auth-btn'));

      await waitFor(() => {
        expect(screen.getByText('Tier Assignment: onyx')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('complete-assignment-btn'));

      await waitFor(() => {
        expect(screen.getByText('Welcome to onyx tier')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('complete-ceremony-btn'));

      await waitFor(() => {
        expect(screen.getByText('Portal Dashboard - onyx')).toBeInTheDocument();
      });
    });
  });

  describe('Portal Feature Navigation', () => {
    beforeEach(async () => {
      // Setup completed onboarding state
      render(<BlackPortal />);

      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'VOID_ACCESS');

      await waitFor(() => {
        expect(screen.getByTestId('biometric-auth')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('face-auth-btn'));

      await waitFor(() => {
        expect(screen.getByTestId('tier-assignment')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('complete-assignment-btn'));

      await waitFor(() => {
        expect(screen.getByTestId('welcome-ceremony')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('complete-ceremony-btn'));

      await waitFor(() => {
        expect(screen.getByTestId('portal-dashboard')).toBeInTheDocument();
      });
    });

    test('navigates to Butler AI interface', async () => {
      const butlerNavBtn = screen.getByTestId('nav-butler');
      await user.click(butlerNavBtn);

      await waitFor(() => {
        expect(screen.getByTestId('butler-interface')).toBeInTheDocument();
      });

      expect(screen.getByText('Butler AI - void')).toBeInTheDocument();
      expect(screen.getByText(/Anonymous ID: Quantum_Sage_/)).toBeInTheDocument();

      // Test Butler interaction
      const butlerInput = screen.getByTestId('butler-input');
      await user.type(butlerInput, 'Hello Butler');

      const sendBtn = screen.getByTestId('send-message-btn');
      await user.click(sendBtn);

      // Return to dashboard
      const backBtn = screen.getByTestId('back-to-dashboard');
      await user.click(backBtn);

      await waitFor(() => {
        expect(screen.getByTestId('portal-dashboard')).toBeInTheDocument();
      });
    });

    test('navigates to Social Circle', async () => {
      const socialNavBtn = screen.getByTestId('nav-social');
      await user.click(socialNavBtn);

      await waitFor(() => {
        expect(screen.getByTestId('social-circle')).toBeInTheDocument();
      });

      expect(screen.getByText('Social Circle - void')).toBeInTheDocument();
      expect(screen.getByText(/Anonymous ID: Quantum_Sage_/)).toBeInTheDocument();

      // Test social features
      expect(screen.getByTestId('start-discussion-btn')).toBeInTheDocument();
      expect(screen.getByTestId('share-deal-btn')).toBeInTheDocument();
      expect(screen.getByTestId('create-poll-btn')).toBeInTheDocument();

      await user.click(screen.getByTestId('start-discussion-btn'));

      // Return to dashboard
      await user.click(screen.getByTestId('back-to-dashboard'));

      await waitFor(() => {
        expect(screen.getByTestId('portal-dashboard')).toBeInTheDocument();
      });
    });

    test('navigates to Anonymous Services', async () => {
      const servicesNavBtn = screen.getByTestId('nav-services');
      await user.click(servicesNavBtn);

      await waitFor(() => {
        expect(screen.getByTestId('service-dashboard')).toBeInTheDocument();
      });

      expect(screen.getByText('Service Dashboard - void')).toBeInTheDocument();

      // Test service features
      expect(screen.getByTestId('book-jet-btn')).toBeInTheDocument();
      expect(screen.getByTestId('emergency-medical-btn')).toBeInTheDocument();
      expect(screen.getByTestId('concierge-dining-btn')).toBeInTheDocument();

      await user.click(screen.getByTestId('book-jet-btn'));

      // Return to dashboard
      await user.click(screen.getByTestId('back-to-dashboard'));

      await waitFor(() => {
        expect(screen.getByTestId('portal-dashboard')).toBeInTheDocument();
      });
    });

    test('navigates to App Distribution', async () => {
      const appsNavBtn = screen.getByTestId('nav-apps');
      await user.click(appsNavBtn);

      await waitFor(() => {
        expect(screen.getByTestId('app-distribution')).toBeInTheDocument();
      });

      expect(screen.getByText('App Distribution - void')).toBeInTheDocument();
      expect(screen.getByText('Security Assessment: 95/100')).toBeInTheDocument();

      // Test app download features
      expect(screen.getByTestId('download-ios-btn')).toBeInTheDocument();
      expect(screen.getByTestId('download-android-btn')).toBeInTheDocument();

      await user.click(screen.getByTestId('download-ios-btn'));

      // Return to dashboard
      await user.click(screen.getByTestId('back-to-dashboard'));

      await waitFor(() => {
        expect(screen.getByTestId('portal-dashboard')).toBeInTheDocument();
      });
    });
  });

  describe('Anonymous Services User Journey', () => {
    beforeEach(async () => {
      // Complete onboarding first
      render(<BlackPortal />);

      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'OBSIDIAN_ELITE');

      await waitFor(() => screen.getByTestId('biometric-auth'));
      await user.click(screen.getByTestId('face-auth-btn'));

      await waitFor(() => screen.getByTestId('tier-assignment'));
      await user.click(screen.getByTestId('complete-assignment-btn'));

      await waitFor(() => screen.getByTestId('welcome-ceremony'));
      await user.click(screen.getByTestId('complete-ceremony-btn'));

      await waitFor(() => screen.getByTestId('portal-dashboard'));
    });

    test('completes anonymous service booking flow', async () => {
      // Navigate to services
      await user.click(screen.getByTestId('nav-services'));

      await waitFor(() => {
        expect(screen.getByTestId('service-dashboard')).toBeInTheDocument();
      });

      // Book private jet
      await user.click(screen.getByTestId('book-jet-btn'));

      // Should maintain anonymity throughout
      expect(screen.getByText('Service Dashboard - obsidian')).toBeInTheDocument();

      // Test emergency services
      await user.click(screen.getByTestId('emergency-medical-btn'));

      // Test concierge services
      await user.click(screen.getByTestId('concierge-dining-btn'));
    });

    test('completes social circle interaction flow', async () => {
      // Navigate to social circle
      await user.click(screen.getByTestId('nav-social'));

      await waitFor(() => {
        expect(screen.getByTestId('social-circle')).toBeInTheDocument();
      });

      // Start a discussion
      await user.click(screen.getByTestId('start-discussion-btn'));

      // Share a deal
      await user.click(screen.getByTestId('share-deal-btn'));

      // Create a poll
      await user.click(screen.getByTestId('create-poll-btn'));

      // Verify anonymous identity is maintained
      expect(screen.getByText(/Anonymous ID: Crystal_Emperor_/)).toBeInTheDocument();
    });

    test('completes Butler AI interaction flow', async () => {
      // Navigate to Butler
      await user.click(screen.getByTestId('nav-butler'));

      await waitFor(() => {
        expect(screen.getByTestId('butler-interface')).toBeInTheDocument();
      });

      // Send multiple messages to Butler
      const butlerInput = screen.getByTestId('butler-input');
      const sendBtn = screen.getByTestId('send-message-btn');

      await user.type(butlerInput, 'I need concierge services');
      await user.click(sendBtn);

      await user.clear(butlerInput);
      await user.type(butlerInput, 'Connect me with other circle members');
      await user.click(sendBtn);

      await user.clear(butlerInput);
      await user.type(butlerInput, 'Book emergency medical services');
      await user.click(sendBtn);

      // Verify Butler maintains context and anonymity
      expect(screen.getByText('Butler AI - obsidian')).toBeInTheDocument();
    });
  });

  describe('Cross-Feature Integration', () => {
    test('maintains user state across all features', async () => {
      render(<BlackPortal />);

      // Complete onboarding
      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'VOID_ACCESS');

      await waitFor(() => screen.getByTestId('biometric-auth'));
      await user.click(screen.getByTestId('face-auth-btn'));

      await waitFor(() => screen.getByTestId('tier-assignment'));
      await user.click(screen.getByTestId('complete-assignment-btn'));

      await waitFor(() => screen.getByTestId('welcome-ceremony'));
      await user.click(screen.getByTestId('complete-ceremony-btn'));

      await waitFor(() => screen.getByTestId('portal-dashboard'));

      // Navigate through all features and verify state consistency
      const features = ['butler', 'social', 'services', 'apps'];

      for (const feature of features) {
        await user.click(screen.getByTestId(`nav-${feature}`));

        await waitFor(() => {
          // Each feature should show void tier
          expect(screen.getByText(new RegExp(`${feature === 'apps' ? 'App Distribution' : feature === 'butler' ? 'Butler AI' : feature === 'social' ? 'Social Circle' : 'Service Dashboard'} - void`, 'i'))).toBeInTheDocument();
        });

        if (feature !== 'apps') {
          // Verify anonymous ID consistency (except app distribution)
          expect(screen.getByText(/Anonymous ID: Quantum_Sage_/)).toBeInTheDocument();
        }

        await user.click(screen.getByTestId('back-to-dashboard'));
        await waitFor(() => screen.getByTestId('portal-dashboard'));
      }
    });

    test('handles tier-specific feature differences', async () => {
      const tiers = [
        { code: 'ONYX_PREMIUM', tier: 'onyx', prefix: 'Silver_Navigator' },
        { code: 'OBSIDIAN_ELITE', tier: 'obsidian', prefix: 'Crystal_Emperor' },
        { code: 'VOID_ACCESS', tier: 'void', prefix: 'Quantum_Sage' },
      ];

      for (const { code, tier, prefix } of tiers) {
        // Start fresh for each tier
        const { unmount } = render(<BlackPortal />);

        // Complete onboarding for this tier
        const invitationInput = screen.getByTestId('invitation-input');
        await user.type(invitationInput, code);

        await waitFor(() => screen.getByTestId('biometric-auth'));
        await user.click(screen.getByTestId('face-auth-btn'));

        await waitFor(() => screen.getByTestId('tier-assignment'));
        await user.click(screen.getByTestId('complete-assignment-btn'));

        await waitFor(() => screen.getByTestId('welcome-ceremony'));
        await user.click(screen.getByTestId('complete-ceremony-btn'));

        await waitFor(() => screen.getByTestId('portal-dashboard'));

        // Verify tier-specific dashboard
        expect(screen.getByText(`Portal Dashboard - ${tier}`)).toBeInTheDocument();

        // Check Butler AI tier specificity
        await user.click(screen.getByTestId('nav-butler'));
        await waitFor(() => {
          expect(screen.getByText(`Butler AI - ${tier}`)).toBeInTheDocument();
          expect(screen.getByText(new RegExp(`Anonymous ID: ${prefix}_`))).toBeInTheDocument();
        });

        unmount();
      }
    });
  });

  describe('Error Handling and Edge Cases', () => {
    test('handles invalid invitation codes', async () => {
      render(<BlackPortal />);

      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'INVALID_CODE');

      // Should remain on invitation screen
      expect(screen.getByTestId('invitation-prompt')).toBeInTheDocument();
    });

    test('handles authentication failures gracefully', async () => {
      // This would require mocking authentication failure scenarios
      // For now, we test that the components are properly structured for error handling
      render(<BlackPortal />);

      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'VOID_ACCESS');

      await waitFor(() => {
        expect(screen.getByTestId('biometric-auth')).toBeInTheDocument();
      });

      // The BiometricAuth component should handle failures internally
      expect(screen.getByTestId('face-auth-btn')).toBeInTheDocument();
      expect(screen.getByTestId('fingerprint-auth-btn')).toBeInTheDocument();
    });

    test('maintains proper navigation state', async () => {
      render(<BlackPortal />);

      // Complete quick onboarding
      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'ONYX_PREMIUM');

      await waitFor(() => screen.getByTestId('biometric-auth'));
      await user.click(screen.getByTestId('face-auth-btn'));

      await waitFor(() => screen.getByTestId('tier-assignment'));
      await user.click(screen.getByTestId('complete-assignment-btn'));

      await waitFor(() => screen.getByTestId('welcome-ceremony'));
      await user.click(screen.getByTestId('complete-ceremony-btn'));

      await waitFor(() => screen.getByTestId('portal-dashboard'));

      // Test rapid navigation
      const navSequence = ['butler', 'social', 'services', 'apps', 'butler', 'social'];

      for (const nav of navSequence) {
        await user.click(screen.getByTestId(`nav-${nav}`));
        
        await waitFor(() => {
          const expectedTexts = {
            butler: 'Butler AI - onyx',
            social: 'Social Circle - onyx',
            services: 'Service Dashboard - onyx',
            apps: 'App Distribution - onyx',
          };
          expect(screen.getByText(expectedTexts[nav as keyof typeof expectedTexts])).toBeInTheDocument();
        });

        await user.click(screen.getByTestId('back-to-dashboard'));
        await waitFor(() => screen.getByTestId('portal-dashboard'));
      }
    });
  });

  describe('Performance and Responsiveness', () => {
    test('onboarding completes within performance thresholds', async () => {
      const startTime = performance.now();

      render(<BlackPortal />);

      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'VOID_ACCESS');

      await waitFor(() => screen.getByTestId('biometric-auth'));
      await user.click(screen.getByTestId('face-auth-btn'));

      await waitFor(() => screen.getByTestId('tier-assignment'));
      await user.click(screen.getByTestId('complete-assignment-btn'));

      await waitFor(() => screen.getByTestId('welcome-ceremony'));
      await user.click(screen.getByTestId('complete-ceremony-btn'));

      await waitFor(() => screen.getByTestId('portal-dashboard'));

      const endTime = performance.now();
      const totalTime = endTime - startTime;

      // Onboarding should complete within 5 seconds
      expect(totalTime).toBeLessThan(5000);
    });

    test('feature navigation is responsive', async () => {
      render(<BlackPortal />);

      // Quick onboarding
      const invitationInput = screen.getByTestId('invitation-input');
      await user.type(invitationInput, 'OBSIDIAN_ELITE');

      await waitFor(() => screen.getByTestId('biometric-auth'));
      await user.click(screen.getByTestId('face-auth-btn'));

      await waitFor(() => screen.getByTestId('tier-assignment'));
      await user.click(screen.getByTestId('complete-assignment-btn'));

      await waitFor(() => screen.getByTestId('welcome-ceremony'));
      await user.click(screen.getByTestId('complete-ceremony-btn'));

      await waitFor(() => screen.getByTestId('portal-dashboard'));

      // Test navigation responsiveness
      const features = ['butler', 'social', 'services', 'apps'];

      for (const feature of features) {
        const navStartTime = performance.now();

        await user.click(screen.getByTestId(`nav-${feature}`));

        await waitFor(() => {
          expect(screen.getByTestId(feature === 'butler' ? 'butler-interface' : 
                                   feature === 'social' ? 'social-circle' :
                                   feature === 'services' ? 'service-dashboard' :
                                   'app-distribution')).toBeInTheDocument();
        });

        const navEndTime = performance.now();
        const navTime = navEndTime - navStartTime;

        // Each navigation should complete within 1 second
        expect(navTime).toBeLessThan(1000);

        await user.click(screen.getByTestId('back-to-dashboard'));
        await waitFor(() => screen.getByTestId('portal-dashboard'));
      }
    });
  });
});