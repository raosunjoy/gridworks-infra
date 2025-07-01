/**
 * Concierge Services Request Interface
 * Ultra-luxury concierge service request system with anonymous delivery,
 * private aviation, art acquisition, and exclusive experiences
 */

import React, { useState, useEffect } from 'react';
import { ConciergeCategory, ServiceTier, ConciergeRequest } from '../../services/EnhancedConciergeServices';
import { LuxuryCard } from '../ui/LuxuryCard';
import { TierGlow } from '../ui/TierGlow';

interface ConciergeServicesInterfaceProps {
  tier: ServiceTier;
  anonymousId: string;
}

interface ServiceRequest {
  category: ConciergeCategory;
  title: string;
  description: string;
  urgencyLevel: 'standard' | 'priority' | 'emergency' | 'impossible';
  specifications: Record<string, any>;
  budget: {
    range: 'no_limit' | 'ultra_high' | 'high' | 'premium';
    maxBudget?: number;
  };
  anonymityRequirements: {
    identityConcealment: 'standard' | 'enhanced' | 'absolute';
    publicityRestrictions: string[];
    communicationProtocol: 'anonymous' | 'pseudonym' | 'representative';
  };
}

const conciergeCategories = [
  {
    key: ConciergeCategory.PRIVATE_AVIATION,
    title: 'Private Aviation',
    description: 'Private jets, helicopters, and exclusive air travel',
    icon: '✈️',
    minBudget: 50000000, // ₹5 Cr
  },
  {
    key: ConciergeCategory.ART_ACQUISITION,
    title: 'Art Acquisition',
    description: 'Museum-quality art and collectibles sourcing',
    icon: '🎨',
    minBudget: 100000000, // ₹10 Cr
  },
  {
    key: ConciergeCategory.LUXURY_ACCOMMODATION,
    title: 'Luxury Accommodation',
    description: 'Ultra-exclusive hotels and private residences',
    icon: '🏰',
    minBudget: 20000000, // ₹2 Cr
  },
  {
    key: ConciergeCategory.GOLDEN_VISA,
    title: 'Golden Visa Programs',
    description: 'Citizenship and residency by investment',
    icon: '🛂',
    minBudget: 500000000, // ₹50 Cr
  },
  {
    key: ConciergeCategory.YACHT_CHARTER,
    title: 'Yacht Charter',
    description: 'Luxury yacht charters and acquisitions',
    icon: '🛥️',
    minBudget: 100000000, // ₹10 Cr
  },
  {
    key: ConciergeCategory.PRIVATE_CHEF,
    title: 'Private Chef Services',
    description: 'Michelin-star chefs and culinary experiences',
    icon: '👨‍🍳',
    minBudget: 5000000, // ₹50 L
  },
  {
    key: ConciergeCategory.SECURITY_SERVICES,
    title: 'Security Services',
    description: 'Personal protection and security consulting',
    icon: '🛡️',
    minBudget: 30000000, // ₹3 Cr
  },
  {
    key: ConciergeCategory.WELLNESS_RETREATS,
    title: 'Wellness Retreats',
    description: 'Exclusive wellness and medical tourism',
    icon: '🧘‍♀️',
    minBudget: 50000000, // ₹5 Cr
  },
  {
    key: ConciergeCategory.EXCLUSIVE_EVENTS,
    title: 'Exclusive Events',
    description: 'VIP access and private event coordination',
    icon: '🎭',
    minBudget: 25000000, // ₹2.5 Cr
  },
  {
    key: ConciergeCategory.EDUCATIONAL_SERVICES,
    title: 'Educational Services',
    description: 'Elite education and tutoring services',
    icon: '🎓',
    minBudget: 10000000, // ₹1 Cr
  },
];

export const ConciergeServicesInterface: React.FC<ConciergeServicesInterfaceProps> = ({
  tier,
  anonymousId,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<ConciergeCategory | null>(null);
  const [serviceRequest, setServiceRequest] = useState<Partial<ServiceRequest>>({
    urgencyLevel: 'standard',
    budget: { range: 'high' },
    anonymityRequirements: {
      identityConcealment: tier === 'void' ? 'absolute' : tier === 'obsidian' ? 'enhanced' : 'standard',
      publicityRestrictions: ['No media coverage', 'No public records'],
      communicationProtocol: 'anonymous',
    },
    specifications: {},
  });
  const [activeRequests, setActiveRequests] = useState<ConciergeRequest[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadActiveRequests();
  }, [anonymousId]);

  const loadActiveRequests = async () => {
    // In real implementation, this would load from EnhancedConciergeServices
    const mockRequests: ConciergeRequest[] = [
      {
        id: 'req-private-jet-001',
        clientId: 'anonymous-client',
        anonymousId,
        tier,
        category: ConciergeCategory.PRIVATE_AVIATION,
        title: 'Private Jet to Dubai',
        description: 'Immediate private jet charter from Mumbai to Dubai for 6 passengers',
        urgencyLevel: 'priority',
        specifications: {
          dates: { preferred: ['2024-07-01'], flexible: false, duration: '3 hours' },
          location: { departure: 'Mumbai', destination: 'Dubai' },
          guests: { adults: 4, children: 2 },
          preferences: { aircraftType: 'Heavy Jet', amenities: ['Full meal service', 'WiFi'] },
        },
        anonymityRequirements: {
          identityConcealment: 'enhanced',
          publicityRestrictions: ['No flight logs', 'No passenger manifest'],
          documentationLimits: ['Minimal customs documentation'],
          communicationProtocol: 'anonymous',
        },
        status: 'in_progress',
        assignedConcierge: 'Sterling-Aviation-007',
        estimatedCompletion: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
        createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];
    setActiveRequests(mockRequests);
  };

  const formatCurrency = (amount: number) => {
    const crores = amount / 10000000;
    return `₹${crores.toLocaleString('en-IN')} Cr`;
  };

  const handleCategorySelect = (category: ConciergeCategory) => {
    setSelectedCategory(category);
    setServiceRequest({
      ...serviceRequest,
      category,
      title: '',
      description: '',
      specifications: getDefaultSpecifications(category),
    });
  };

  const getDefaultSpecifications = (category: ConciergeCategory) => {
    switch (category) {
      case ConciergeCategory.PRIVATE_AVIATION:
        return {
          dates: { preferred: [], flexible: true, duration: '' },
          location: { departure: '', destination: '' },
          guests: { adults: 1, children: 0 },
          aircraftType: 'mid_size',
          amenities: [],
        };
      case ConciergeCategory.ART_ACQUISITION:
        return {
          artType: '',
          artist: '',
          priceRange: '',
          timeframe: 'no_rush',
          authentication: 'required',
          delivery: 'anonymous',
        };
      case ConciergeCategory.LUXURY_ACCOMMODATION:
        return {
          location: '',
          checkIn: '',
          checkOut: '',
          guests: { adults: 1, children: 0 },
          propertyType: 'hotel',
          amenities: [],
        };
      case ConciergeCategory.GOLDEN_VISA:
        return {
          targetCountries: [],
          investmentType: 'real_estate',
          familyMembers: 1,
          timeline: '6-12 months',
        };
      default:
        return {};
    }
  };

  const submitRequest = async () => {
    if (!selectedCategory || !serviceRequest.title || !serviceRequest.description) {
      return;
    }

    setIsSubmitting(true);
    try {
      // In real implementation, this would call EnhancedConciergeServices
      const newRequest: ConciergeRequest = {
        id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
        clientId: 'anonymous-client',
        anonymousId,
        tier,
        category: selectedCategory,
        title: serviceRequest.title!,
        description: serviceRequest.description!,
        urgencyLevel: serviceRequest.urgencyLevel!,
        specifications: serviceRequest.specifications!,
        anonymityRequirements: serviceRequest.anonymityRequirements!,
        status: 'received',
        assignedConcierge: '',
        estimatedCompletion: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      setActiveRequests([...activeRequests, newRequest]);
      setSelectedCategory(null);
      setServiceRequest({
        urgencyLevel: 'standard',
        budget: { range: 'high' },
        anonymityRequirements: {
          identityConcealment: tier === 'void' ? 'absolute' : tier === 'obsidian' ? 'enhanced' : 'standard',
          publicityRestrictions: ['No media coverage', 'No public records'],
          communicationProtocol: 'anonymous',
        },
        specifications: {},
      });
    } catch (error) {
      console.error('Failed to submit concierge request:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getTierColor = (tier: ServiceTier) => {
    switch (tier) {
      case 'onyx': return 'from-slate-600 to-slate-900';
      case 'obsidian': return 'from-purple-600 to-purple-900';
      case 'void': return 'from-black to-gray-900';
      default: return 'from-gray-600 to-gray-900';
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'standard': return 'text-green-400';
      case 'priority': return 'text-yellow-400';
      case 'emergency': return 'text-orange-400';
      case 'impossible': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const renderCategoryGrid = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {conciergeCategories.map((category) => (
        <LuxuryCard
          key={category.key}
          className="group cursor-pointer transform transition-all duration-300 hover:scale-105"
          onClick={() => handleCategorySelect(category.key)}
        >
          <div className="p-6 text-center">
            <div className="text-4xl mb-4">{category.icon}</div>
            <h3 className="text-lg font-bold mb-2 group-hover:text-gold-400 transition-colors">
              {category.title}
            </h3>
            <p className="text-gray-400 text-sm mb-4">{category.description}</p>
            <div className="text-gold-400 text-sm font-medium">
              From {formatCurrency(category.minBudget)}
            </div>
          </div>
        </LuxuryCard>
      ))}
    </div>
  );

  const renderPrivateAviationForm = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Departure Location</label>
          <input
            type="text"
            value={serviceRequest.specifications?.location?.departure || ''}
            onChange={(e) => setServiceRequest({
              ...serviceRequest,
              specifications: {
                ...serviceRequest.specifications,
                location: { ...serviceRequest.specifications?.location, departure: e.target.value }
              }
            })}
            className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                     focus:border-gold-500 focus:outline-none"
            placeholder="Mumbai, Delhi, Bangalore..."
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Destination</label>
          <input
            type="text"
            value={serviceRequest.specifications?.location?.destination || ''}
            onChange={(e) => setServiceRequest({
              ...serviceRequest,
              specifications: {
                ...serviceRequest.specifications,
                location: { ...serviceRequest.specifications?.location, destination: e.target.value }
              }
            })}
            className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                     focus:border-gold-500 focus:outline-none"
            placeholder="Dubai, Singapore, London..."
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Adults</label>
          <input
            type="number"
            min="1"
            max="20"
            value={serviceRequest.specifications?.guests?.adults || 1}
            onChange={(e) => setServiceRequest({
              ...serviceRequest,
              specifications: {
                ...serviceRequest.specifications,
                guests: { ...serviceRequest.specifications?.guests, adults: parseInt(e.target.value) }
              }
            })}
            className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                     focus:border-gold-500 focus:outline-none"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Children</label>
          <input
            type="number"
            min="0"
            max="10"
            value={serviceRequest.specifications?.guests?.children || 0}
            onChange={(e) => setServiceRequest({
              ...serviceRequest,
              specifications: {
                ...serviceRequest.specifications,
                guests: { ...serviceRequest.specifications?.guests, children: parseInt(e.target.value) }
              }
            })}
            className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                     focus:border-gold-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Aircraft Type</label>
          <select
            value={serviceRequest.specifications?.aircraftType || 'mid_size'}
            onChange={(e) => setServiceRequest({
              ...serviceRequest,
              specifications: { ...serviceRequest.specifications, aircraftType: e.target.value }
            })}
            className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                     focus:border-gold-500 focus:outline-none"
          >
            <option value="light_jet">Light Jet</option>
            <option value="mid_size">Mid-Size Jet</option>
            <option value="heavy_jet">Heavy Jet</option>
            <option value="ultra_long_range">Ultra Long Range</option>
            <option value="airliner">Private Airliner</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Special Requirements</label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {['Full meal service', 'WiFi', 'Entertainment system', 'Conference setup', 'Medical equipment', 'Pet accommodation'].map((amenity) => (
            <label key={amenity} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={serviceRequest.specifications?.amenities?.includes(amenity)}
                onChange={(e) => {
                  const current = serviceRequest.specifications?.amenities || [];
                  const updated = e.target.checked
                    ? [...current, amenity]
                    : current.filter(a => a !== amenity);
                  setServiceRequest({
                    ...serviceRequest,
                    specifications: { ...serviceRequest.specifications, amenities: updated }
                  });
                }}
                className="rounded border-gold-500/30 bg-black/50 text-gold-500 focus:ring-gold-500"
              />
              <span className="text-sm text-gray-300">{amenity}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );

  const renderRequestForm = () => (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={() => setSelectedCategory(null)}
          className="text-gray-400 hover:text-white transition-colors"
        >
          ← Back to Categories
        </button>
        <div>
          <h2 className="text-2xl font-bold text-white">
            {conciergeCategories.find(c => c.key === selectedCategory)?.title}
          </h2>
          <p className="text-gray-400">
            {conciergeCategories.find(c => c.key === selectedCategory)?.description}
          </p>
        </div>
      </div>

      <LuxuryCard className="p-8">
        <div className="space-y-6">
          {/* Basic Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Request Title</label>
              <input
                type="text"
                value={serviceRequest.title || ''}
                onChange={(e) => setServiceRequest({ ...serviceRequest, title: e.target.value })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
                placeholder="Brief title for your request"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Urgency Level</label>
              <select
                value={serviceRequest.urgencyLevel}
                onChange={(e) => setServiceRequest({ 
                  ...serviceRequest, 
                  urgencyLevel: e.target.value as 'standard' | 'priority' | 'emergency' | 'impossible'
                })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
              >
                <option value="standard">Standard (7-14 days)</option>
                <option value="priority">Priority (1-3 days)</option>
                <option value="emergency">Emergency (24 hours)</option>
                {tier === 'void' && <option value="impossible">Impossible (Immediate)</option>}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Detailed Description</label>
            <textarea
              rows={4}
              value={serviceRequest.description || ''}
              onChange={(e) => setServiceRequest({ ...serviceRequest, description: e.target.value })}
              className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                       focus:border-gold-500 focus:outline-none resize-none"
              placeholder="Provide detailed requirements for your request..."
            />
          </div>

          {/* Category-specific forms */}
          {selectedCategory === ConciergeCategory.PRIVATE_AVIATION && renderPrivateAviationForm()}

          {/* Budget */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Budget Range</label>
            <select
              value={serviceRequest.budget?.range}
              onChange={(e) => setServiceRequest({
                ...serviceRequest,
                budget: { ...serviceRequest.budget, range: e.target.value as any }
              })}
              className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                       focus:border-gold-500 focus:outline-none"
            >
              <option value="premium">Premium (₹1-10 Cr)</option>
              <option value="high">High (₹10-50 Cr)</option>
              <option value="ultra_high">Ultra High (₹50-500 Cr)</option>
              {tier !== 'onyx' && <option value="no_limit">No Limit</option>}
            </select>
          </div>

          {/* Anonymity Requirements */}
          <div className="space-y-4">
            <h4 className="font-semibold text-gold-400">Anonymity & Privacy</h4>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Identity Concealment</label>
              <select
                value={serviceRequest.anonymityRequirements?.identityConcealment}
                onChange={(e) => setServiceRequest({
                  ...serviceRequest,
                  anonymityRequirements: {
                    ...serviceRequest.anonymityRequirements!,
                    identityConcealment: e.target.value as 'standard' | 'enhanced' | 'absolute'
                  }
                })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
              >
                <option value="standard">Standard (Basic privacy)</option>
                <option value="enhanced">Enhanced (Multiple layers)</option>
                {tier !== 'onyx' && <option value="absolute">Absolute (Complete anonymity)</option>}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Communication Protocol</label>
              <select
                value={serviceRequest.anonymityRequirements?.communicationProtocol}
                onChange={(e) => setServiceRequest({
                  ...serviceRequest,
                  anonymityRequirements: {
                    ...serviceRequest.anonymityRequirements!,
                    communicationProtocol: e.target.value as 'anonymous' | 'pseudonym' | 'representative'
                  }
                })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
              >
                <option value="anonymous">Anonymous messaging only</option>
                <option value="pseudonym">Pseudonym communications</option>
                <option value="representative">Designated representative</option>
              </select>
            </div>
          </div>

          {/* Submit Button */}
          <button
            onClick={submitRequest}
            disabled={isSubmitting || !serviceRequest.title || !serviceRequest.description}
            className="w-full py-4 bg-gradient-to-r from-gold-500 to-gold-600 text-black font-bold rounded-lg
                     hover:from-gold-400 hover:to-gold-500 transition-all duration-300 disabled:opacity-50
                     disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Submitting Request...' : 'Submit Concierge Request'}
          </button>
        </div>
      </LuxuryCard>
    </div>
  );

  const renderActiveRequests = () => (
    <div className="space-y-4">
      <h3 className="text-xl font-bold">Active Requests</h3>
      {activeRequests.length === 0 ? (
        <LuxuryCard className="p-8 text-center">
          <div className="text-gray-400 mb-4">No active concierge requests</div>
          <div className="text-sm text-gray-500">Your requests will appear here once submitted</div>
        </LuxuryCard>
      ) : (
        <div className="space-y-4">
          {activeRequests.map((request) => (
            <LuxuryCard key={request.id} className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h4 className="text-lg font-semibold text-white">{request.title}</h4>
                    <span className={`px-2 py-1 text-xs rounded-full ${getUrgencyColor(request.urgencyLevel)} bg-current bg-opacity-20`}>
                      {request.urgencyLevel.toUpperCase()}
                    </span>
                    <span className="px-2 py-1 text-xs rounded-full bg-gray-600 text-gray-300">
                      {request.category.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  
                  <p className="text-gray-400 mb-3">{request.description}</p>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Status:</span>
                      <div className="text-white font-medium capitalize">{request.status.replace('_', ' ')}</div>
                    </div>
                    <div>
                      <span className="text-gray-400">Concierge:</span>
                      <div className="text-white font-medium">{request.assignedConcierge || 'Assigning...'}</div>
                    </div>
                    <div>
                      <span className="text-gray-400">Created:</span>
                      <div className="text-white font-medium">
                        {new Date(request.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-400">Estimated:</span>
                      <div className="text-white font-medium">
                        {new Date(request.estimatedCompletion).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
                
                <button className="ml-4 px-4 py-2 bg-gold-500/20 text-gold-400 rounded-lg hover:bg-gold-500/30 transition-colors">
                  View Details
                </button>
              </div>
            </LuxuryCard>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gold-400 to-gold-600 bg-clip-text text-transparent">
          Concierge Services
        </h1>
        <p className="text-lg text-gray-300">
          Ultra-luxury services with complete anonymity • {tier.toUpperCase()} Tier
        </p>
      </div>

      {/* Navigation */}
      <div className="flex justify-center">
        <nav className="flex space-x-1 bg-black/50 rounded-lg p-1">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-6 py-3 rounded-lg transition-all duration-200 ${
              !selectedCategory
                ? 'bg-gold-500 text-black font-medium'
                : 'text-gray-300 hover:text-white hover:bg-white/10'
            }`}
          >
            All Services
          </button>
          <button className="px-6 py-3 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 transition-all duration-200">
            Active Requests ({activeRequests.length})
          </button>
        </nav>
      </div>

      {/* Content */}
      {!selectedCategory ? (
        <div className="space-y-8">
          {renderCategoryGrid()}
          {renderActiveRequests()}
        </div>
      ) : (
        renderRequestForm()
      )}
    </div>
  );
};