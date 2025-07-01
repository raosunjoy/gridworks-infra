'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LuxuryService } from '@/types/butler';
import { BlackUser } from '@/types/portal';
import { useLuxuryEffects } from '@/hooks/useLuxuryEffects';

interface ConciergeServicesProps {
  user: BlackUser;
  isOpen: boolean;
  onClose: () => void;
}

interface ServiceRequest {
  id: string;
  serviceId: string;
  serviceName: string;
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled';
  requestedDate: Date;
  scheduledDate?: Date;
  specialRequests: string;
  estimatedCost: string;
  conciergeNotes?: string;
}

export function ConciergeServices({ user, isOpen, onClose }: ConciergeServicesProps) {
  const [activeTab, setActiveTab] = useState<'services' | 'bookings' | 'history'>('services');
  const [services, setServices] = useState<LuxuryService[]>([]);
  const [currentRequests, setCurrentRequests] = useState<ServiceRequest[]>([]);
  const [selectedService, setSelectedService] = useState<LuxuryService | null>(null);
  const [showBookingForm, setShowBookingForm] = useState(false);

  const { luxuryInteraction, luxurySuccess, getTierColor } = useLuxuryEffects(user.tier);

  useEffect(() => {
    initializeServices();
    initializeBookings();
  }, [user]);

  const initializeServices = () => {
    const tierServices: LuxuryService[] = [
      // Transportation
      {
        id: 'transport_private_jet',
        name: user.tier === 'void' ? 'Quantum Jet Service' : user.tier === 'obsidian' ? 'Diamond Aviation' : 'Platinum Air',
        category: 'transport',
        tier: user.tier,
        provider: user.tier === 'void' ? 'Interdimensional Airways' : user.tier === 'obsidian' ? 'Crystal Aviation Elite' : 'Silver Sky Services',
        description: user.tier === 'void' 
          ? 'Transcendent travel across space-time dimensions'
          : user.tier === 'obsidian'
          ? 'Ultra-luxury private aviation with crystalline service'
          : 'Premium private jet service with silver-tier amenities',
        priceRange: user.tier === 'void' ? '₹10L - ₹50L per hour' : user.tier === 'obsidian' ? '₹5L - ₹25L per hour' : '₹2L - ₹10L per hour',
        availability: '24/7',
        bookingMethod: 'instant',
        location: 'Global'
      },
      {
        id: 'transport_luxury_car',
        name: user.tier === 'void' ? 'Reality-Bending Vehicles' : user.tier === 'obsidian' ? 'Diamond Fleet' : 'Onyx Motors',
        category: 'transport',
        tier: user.tier,
        provider: 'Luxury Transport Collective',
        description: 'Ultra-premium vehicle fleet with dedicated chauffeur service',
        priceRange: '₹25K - ₹2L per day',
        availability: '24/7',
        bookingMethod: 'instant'
      },
      
      // Hospitality
      {
        id: 'hospitality_hotels',
        name: user.tier === 'void' ? 'Cosmic Residences' : user.tier === 'obsidian' ? 'Crystal Palace Suites' : 'Onyx Luxury Hotels',
        category: 'hospitality',
        tier: user.tier,
        provider: 'Elite Hospitality Network',
        description: 'Exclusive access to the world\'s most luxurious accommodations',
        priceRange: '₹1L - ₹10L per night',
        availability: 'by_appointment',
        bookingMethod: 'concierge_arranged'
      },
      
      // Dining
      {
        id: 'dining_private_chef',
        name: user.tier === 'void' ? 'Quantum Culinary Masters' : user.tier === 'obsidian' ? 'Diamond Chef Experience' : 'Platinum Gastronomy',
        category: 'dining',
        tier: user.tier,
        provider: 'Michelin Elite Collective',
        description: 'World-renowned chefs for exclusive private dining experiences',
        priceRange: '₹2L - ₹15L per event',
        availability: 'by_appointment',
        bookingMethod: 'concierge_arranged'
      },
      {
        id: 'dining_exclusive_restaurants',
        name: 'Ultra-Exclusive Restaurant Access',
        category: 'dining',
        tier: user.tier,
        provider: 'Global Culinary Network',
        description: 'Reserved tables at impossible-to-book restaurants worldwide',
        priceRange: '₹50K - ₹5L per experience',
        availability: 'by_appointment',
        bookingMethod: 'concierge_arranged'
      },
      
      // Entertainment
      {
        id: 'entertainment_events',
        name: user.tier === 'void' ? 'Interdimensional Events' : user.tier === 'obsidian' ? 'Diamond Circle Access' : 'Platinum Entertainment',
        category: 'entertainment',
        tier: user.tier,
        provider: 'Elite Entertainment Network',
        description: 'Exclusive access to private concerts, art exhibitions, and VIP events',
        priceRange: '₹1L - ₹25L per event',
        availability: 'by_appointment',
        bookingMethod: 'concierge_arranged'
      },
      
      // Health & Wellness
      {
        id: 'health_wellness',
        name: user.tier === 'void' ? 'Quantum Wellness Protocols' : user.tier === 'obsidian' ? 'Diamond Health Services' : 'Platinum Wellness',
        category: 'health',
        tier: user.tier,
        provider: 'Elite Wellness Consortium',
        description: 'Premium health, wellness, and spa services at exclusive locations',
        priceRange: '₹75K - ₹10L per session',
        availability: 'by_appointment',
        bookingMethod: 'concierge_arranged'
      }
    ];

    setServices(tierServices);
  };

  const initializeBookings = () => {
    const sampleRequests: ServiceRequest[] = [
      {
        id: 'req_001',
        serviceId: 'transport_private_jet',
        serviceName: 'Private Jet to Dubai',
        status: 'confirmed',
        requestedDate: new Date(Date.now() - 86400000), // 1 day ago
        scheduledDate: new Date(Date.now() + 172800000), // 2 days from now
        specialRequests: 'Vegetarian catering, meeting room setup',
        estimatedCost: '₹15,00,000',
        conciergeNotes: 'G650 confirmed, catering arranged by Michelin-starred chef'
      },
      {
        id: 'req_002',
        serviceId: 'dining_private_chef',
        serviceName: 'Private Chef Experience',
        status: 'in_progress',
        requestedDate: new Date(Date.now() - 43200000), // 12 hours ago
        scheduledDate: new Date(Date.now() + 604800000), // 1 week from now
        specialRequests: 'Japanese cuisine specialist, 12 guests',
        estimatedCost: '₹8,50,000'
      }
    ];

    setCurrentRequests(sampleRequests);
  };

  const getTierConfig = () => {
    switch (user.tier) {
      case 'void':
        return {
          color: '#FFD700',
          accent: '#FFF700',
          bg: 'bg-gradient-to-br from-yellow-900/20 via-gray-900 to-black',
          conciergeTitle: 'QUANTUM CONCIERGE'
        };
      case 'obsidian':
        return {
          color: '#E5E4E2',
          accent: '#F5F5F5',
          bg: 'bg-gradient-to-br from-gray-700/20 via-gray-900 to-black',
          conciergeTitle: 'DIAMOND CONCIERGE'
        };
      case 'onyx':
        return {
          color: '#C0C0C0',
          accent: '#D0D0D0',
          bg: 'bg-gradient-to-br from-gray-600/20 via-gray-900 to-black',
          conciergeTitle: 'PLATINUM CONCIERGE'
        };
      default:
        return {
          color: '#C0C0C0',
          accent: '#D0D0D0',
          bg: 'bg-gradient-to-br from-gray-600/20 via-gray-900 to-black',
          conciergeTitle: 'LUXURY CONCIERGE'
        };
    }
  };

  const tierConfig = getTierConfig();

  const getCategoryIcon = (category: string): string => {
    const icons = {
      transport: '✈️',
      hospitality: '🏨',
      dining: '🍽️',
      entertainment: '🎭',
      health: '💆‍♀️',
      security: '🛡️'
    };
    return icons[category as keyof typeof icons] || '🌟';
  };

  const getStatusColor = (status: string): string => {
    const colors = {
      pending: 'text-yellow-400',
      confirmed: 'text-green-400',
      in_progress: 'text-blue-400',
      completed: 'text-gray-400',
      cancelled: 'text-red-400'
    };
    return colors[status as keyof typeof colors] || 'text-gray-400';
  };

  const handleServiceBooking = (service: LuxuryService) => {
    setSelectedService(service);
    setShowBookingForm(true);
    luxuryInteraction();
  };

  const submitBookingRequest = (formData: any) => {
    const newRequest: ServiceRequest = {
      id: `req_${Date.now()}`,
      serviceId: selectedService!.id,
      serviceName: selectedService!.name,
      status: 'pending',
      requestedDate: new Date(),
      specialRequests: formData.specialRequests || '',
      estimatedCost: 'Calculating...'
    };

    setCurrentRequests(prev => [newRequest, ...prev]);
    setShowBookingForm(false);
    setSelectedService(null);
    luxurySuccess();
  };

  const TabButton = ({ tab, children }: { tab: typeof activeTab, children: React.ReactNode }) => (
    <motion.button
      onClick={() => {
        setActiveTab(tab);
        luxuryInteraction();
      }}
      className={`px-6 py-3 rounded-lg font-luxury-sans tracking-wide transition-all duration-300 ${
        activeTab === tab 
          ? 'text-black shadow-lg' 
          : 'text-gray-400 hover:text-white'
      }`}
      style={{ 
        backgroundColor: activeTab === tab ? tierConfig.color : 'transparent'
      }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {children}
    </motion.button>
  );

  if (!isOpen) return null;

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className={`w-full max-w-6xl h-[90vh] ${tierConfig.bg} border border-gray-700 rounded-xl overflow-hidden shadow-2xl`}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Header */}
        <div className="border-b border-gray-700 p-6 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="text-4xl">🛎️</div>
            <div>
              <h1 className="text-3xl font-luxury-serif" style={{ color: tierConfig.color }}>
                {tierConfig.conciergeTitle}
              </h1>
              <p className="text-gray-400 font-luxury-sans">
                Luxury lifestyle management at your service
              </p>
            </div>
          </div>
          
          <motion.button
            onClick={onClose}
            className="p-3 text-gray-400 hover:text-white transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </motion.button>
        </div>

        {/* Navigation */}
        <div className="border-b border-gray-700 p-6">
          <div className="flex space-x-4">
            <TabButton tab="services">Available Services</TabButton>
            <TabButton tab="bookings">Current Bookings</TabButton>
            <TabButton tab="history">Service History</TabButton>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <AnimatePresence mode="wait">
            {activeTab === 'services' && (
              <motion.div
                key="services"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                {/* Service Categories */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {services.map((service) => (
                    <motion.div
                      key={service.id}
                      className="bg-gray-800 border border-gray-600 rounded-lg p-6 hover:border-gray-500 transition-all"
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="text-3xl">{getCategoryIcon(service.category)}</div>
                        <span 
                          className="px-2 py-1 rounded text-xs font-bold uppercase"
                          style={{ backgroundColor: `${tierConfig.color}20`, color: tierConfig.color }}
                        >
                          {service.tier}
                        </span>
                      </div>
                      
                      <h3 className="text-lg font-luxury-serif text-white mb-2">
                        {service.name}
                      </h3>
                      
                      <p className="text-gray-400 font-luxury-sans text-sm mb-4 leading-relaxed">
                        {service.description}
                      </p>
                      
                      <div className="space-y-2 text-sm mb-4">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Provider:</span>
                          <span className="text-gray-300">{service.provider}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Price Range:</span>
                          <span className="text-gray-300">{service.priceRange}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Availability:</span>
                          <span className="text-gray-300 capitalize">
                            {service.availability.replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                      
                      <motion.button
                        onClick={() => handleServiceBooking(service)}
                        className="w-full py-2 rounded-lg font-luxury-sans transition-all"
                        style={{ 
                          backgroundColor: tierConfig.color,
                          color: '#000'
                        }}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        Request Service
                      </motion.button>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'bookings' && (
              <motion.div
                key="bookings"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <h3 className="text-xl font-luxury-serif" style={{ color: tierConfig.color }}>
                  Current Service Requests
                </h3>
                
                {currentRequests.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">🛎️</div>
                    <p className="text-gray-400 font-luxury-sans">
                      No active service requests. Browse our services to make a booking.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {currentRequests.map((request) => (
                      <motion.div
                        key={request.id}
                        className="bg-gray-800 border border-gray-600 rounded-lg p-6"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        whileHover={{ scale: 1.01 }}
                      >
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h4 className="text-lg font-luxury-serif text-white mb-1">
                              {request.serviceName}
                            </h4>
                            <p className="text-sm text-gray-400">
                              Requested: {request.requestedDate.toLocaleDateString()}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${getStatusColor(request.status)}`}>
                              {request.status.replace('_', ' ')}
                            </span>
                            <div className="text-sm text-gray-400 mt-1">
                              {request.estimatedCost}
                            </div>
                          </div>
                        </div>
                        
                        {request.scheduledDate && (
                          <div className="mb-3">
                            <span className="text-gray-500">Scheduled: </span>
                            <span className="text-green-400">
                              {request.scheduledDate.toLocaleDateString()} at {request.scheduledDate.toLocaleTimeString()}
                            </span>
                          </div>
                        )}
                        
                        {request.specialRequests && (
                          <div className="mb-3">
                            <span className="text-gray-500">Special Requests: </span>
                            <span className="text-gray-300">{request.specialRequests}</span>
                          </div>
                        )}
                        
                        {request.conciergeNotes && (
                          <div className="bg-gray-700/50 rounded-lg p-3">
                            <span className="text-gray-500">Concierge Notes: </span>
                            <span className="text-gray-300">{request.conciergeNotes}</span>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                )}
              </motion.div>
            )}

            {activeTab === 'history' && (
              <motion.div
                key="history"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <h3 className="text-xl font-luxury-serif" style={{ color: tierConfig.color }}>
                  Service History
                </h3>
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📋</div>
                  <p className="text-gray-400 font-luxury-sans">
                    Your service history will appear here once you complete bookings.
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Booking Form Modal */}
      <AnimatePresence>
        {showBookingForm && selectedService && (
          <motion.div
            className="fixed inset-0 z-60 flex items-center justify-center p-4 bg-black/90"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="w-full max-w-2xl bg-gray-900 border border-gray-700 rounded-lg p-6"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
            >
              <h2 className="text-2xl font-luxury-serif mb-6" style={{ color: tierConfig.color }}>
                Book {selectedService.name}
              </h2>
              
              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                submitBookingRequest({
                  specialRequests: formData.get('specialRequests'),
                  preferredDate: formData.get('preferredDate')
                });
              }}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-300 font-luxury-sans mb-2">
                      Preferred Date & Time
                    </label>
                    <input
                      type="datetime-local"
                      name="preferredDate"
                      className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 font-luxury-sans mb-2">
                      Special Requests
                    </label>
                    <textarea
                      name="specialRequests"
                      rows={4}
                      className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      placeholder="Any special requirements or preferences..."
                    />
                  </div>
                </div>
                
                <div className="flex space-x-4 mt-6">
                  <motion.button
                    type="button"
                    onClick={() => setShowBookingForm(false)}
                    className="flex-1 bg-gray-700 text-gray-300 py-3 rounded-lg font-luxury-sans hover:bg-gray-600 transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Cancel
                  </motion.button>
                  <motion.button
                    type="submit"
                    className="flex-1 py-3 rounded-lg font-luxury-sans"
                    style={{ 
                      backgroundColor: tierConfig.color,
                      color: '#000'
                    }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Submit Request
                  </motion.button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}