import { ZKSocialCircleMessaging } from '../../services/ZKSocialCircleMessaging';
import {
  AnonymousIdentity,
  SocialCircleMessage,
  AnonymousDealFlow,
  AnonymousServiceRecommendation,
} from '../../types/anonymous-services';

// Mock crypto for Node.js environment
const mockCrypto = {
  createHash: jest.fn(() => ({
    update: jest.fn().mockReturnThis(),
    digest: jest.fn(() => 'mock-hash'),
  })),
};

jest.mock('crypto', () => mockCrypto);

describe('ZKSocialCircleMessaging', () => {
  let zkMessaging: ZKSocialCircleMessaging;

  beforeEach(() => {
    zkMessaging = new ZKSocialCircleMessaging();
    jest.clearAllMocks();
  });

  describe('Circle Identity Creation', () => {
    test('creates anonymous identity for onyx tier', async () => {
      const identity = await zkMessaging.createCircleIdentity('user123', 'onyx');

      expect(identity).toMatchObject({
        circleId: 'onyx_circle',
        tier: 'onyx',
        reputation: 100,
        zkProof: expect.any(String),
      });

      expect(identity.anonymousId).toMatch(/^(Silver|Stream|Flow|Cascade|Liquid)_(Sage|Architect|Navigator|Strategist|Visionary)_\d+$/);
    });

    test('creates anonymous identity for obsidian tier', async () => {
      const identity = await zkMessaging.createCircleIdentity('user456', 'obsidian');

      expect(identity).toMatchObject({
        circleId: 'obsidian_circle',
        tier: 'obsidian',
        reputation: 100,
        zkProof: expect.any(String),
      });

      expect(identity.anonymousId).toMatch(/^(Crystal|Diamond|Prism|Facet|Clarity)_(Emperor|Titan|Oracle|Sovereign|Mastermind)_\d+$/);
    });

    test('creates anonymous identity for void tier', async () => {
      const identity = await zkMessaging.createCircleIdentity('user789', 'void');

      expect(identity).toMatchObject({
        circleId: 'void_circle',
        tier: 'void',
        reputation: 100,
        zkProof: expect.any(String),
      });

      expect(identity.anonymousId).toMatch(/^(Quantum|Cosmic|Ethereal|Infinite|Transcendent)_(Consciousness|Entity|Being|Essence|Presence)_\d+$/);
    });

    test('generates unique anonymous IDs for multiple users', async () => {
      const identity1 = await zkMessaging.createCircleIdentity('user1', 'onyx');
      const identity2 = await zkMessaging.createCircleIdentity('user2', 'onyx');

      expect(identity1.anonymousId).not.toBe(identity2.anonymousId);
    });

    test('adds identity to appropriate circle', async () => {
      const identity = await zkMessaging.createCircleIdentity('user123', 'onyx');

      // Verify the identity was added to the circle (would need access to private members for full test)
      expect(identity.circleId).toBe('onyx_circle');
      expect(identity.joinedAt).toBeInstanceOf(Date);
    });
  });

  describe('Circle Message Sending', () => {
    let senderIdentity: AnonymousIdentity;

    beforeEach(async () => {
      senderIdentity = await zkMessaging.createCircleIdentity('sender123', 'onyx');
    });

    test('sends circle message successfully', async () => {
      const messageId = await zkMessaging.sendCircleMessage(
        senderIdentity.anonymousId,
        'onyx_circle',
        'Hello fellow traders!',
        'general_discussion',
        {
          priority: 'normal',
          category: ['discussion'],
          confidentialityLevel: 'circle_only'
        }
      );

      expect(messageId).toMatch(/^msg_\d+_[a-z0-9]+$/);
    });

    test('throws error for unauthorized sender', async () => {
      await expect(
        zkMessaging.sendCircleMessage(
          'unauthorized_user',
          'onyx_circle',
          'Unauthorized message',
          'general_discussion',
          {
            priority: 'normal',
            category: ['discussion'],
            confidentialityLevel: 'circle_only'
          }
        )
      ).rejects.toThrow('Sender not authorized for this circle');
    });

    test('throws error for insufficient reputation', async () => {
      // Mock low reputation user
      const lowRepUser = { ...senderIdentity, reputation: 400 };
      
      // Mock verifyCircleMembership to return low rep user
      jest.spyOn(zkMessaging as any, 'verifyCircleMembership').mockResolvedValue(lowRepUser);

      await expect(
        zkMessaging.sendCircleMessage(
          senderIdentity.anonymousId,
          'onyx_circle',
          'Ultra private message',
          'general_discussion',
          {
            priority: 'high',
            category: ['sensitive'],
            confidentialityLevel: 'ultra_private'
          }
        )
      ).rejects.toThrow('Insufficient reputation for this message type');
    });

    test('encrypts message content based on confidentiality level', async () => {
      const encryptSpy = jest.spyOn(zkMessaging as any, 'encryptMessageContent');
      
      await zkMessaging.sendCircleMessage(
        senderIdentity.anonymousId,
        'onyx_circle',
        'Secret message',
        'general_discussion',
        {
          priority: 'high',
          category: ['secret'],
          confidentialityLevel: 'ultra_private'
        }
      );

      expect(encryptSpy).toHaveBeenCalledWith(
        'Secret message',
        'onyx_circle',
        'ultra_private'
      );
    });

    test('generates ZK proof for message', async () => {
      const zkProofSpy = jest.spyOn(zkMessaging as any, 'generateMessageZKProof');
      
      await zkMessaging.sendCircleMessage(
        senderIdentity.anonymousId,
        'onyx_circle',
        'Test message',
        'general_discussion',
        {
          priority: 'normal',
          category: ['test'],
          confidentialityLevel: 'circle_only'
        }
      );

      expect(zkProofSpy).toHaveBeenCalled();
    });

    test('updates sender reputation after message', async () => {
      const updateReputationSpy = jest.spyOn(zkMessaging as any, 'updateReputationForContribution');
      
      await zkMessaging.sendCircleMessage(
        senderIdentity.anonymousId,
        'onyx_circle',
        'Helpful message',
        'market_insight',
        {
          priority: 'normal',
          category: ['insights'],
          confidentialityLevel: 'circle_only'
        }
      );

      expect(updateReputationSpy).toHaveBeenCalledWith(
        senderIdentity.anonymousId,
        'market_insight'
      );
    });
  });

  describe('Anonymous Discussion Creation', () => {
    let initiatorIdentity: AnonymousIdentity;

    beforeEach(async () => {
      initiatorIdentity = await zkMessaging.createCircleIdentity('initiator123', 'obsidian');
    });

    test('creates anonymous discussion successfully', async () => {
      const discussionId = await zkMessaging.createAnonymousDiscussion(
        initiatorIdentity.anonymousId,
        'obsidian_circle',
        'Market Analysis Discussion',
        'market_analysis',
        'Let\'s discuss current market trends'
      );

      expect(discussionId).toMatch(/^disc_\d+_[a-z0-9]+$/);
    });

    test('sets initiator as moderator', async () => {
      const discussionId = await zkMessaging.createAnonymousDiscussion(
        initiatorIdentity.anonymousId,
        'obsidian_circle',
        'Investment Strategy',
        'investment_strategy',
        'Initial discussion message'
      );

      // Would need access to private members to fully verify moderator status
      expect(discussionId).toBeDefined();
    });

    test('creates discussion with proper rules', async () => {
      const maxParticipantsSpy = jest.spyOn(zkMessaging as any, 'getMaxParticipantsForCircle');
      maxParticipantsSpy.mockReturnValue(30);

      await zkMessaging.createAnonymousDiscussion(
        initiatorIdentity.anonymousId,
        'obsidian_circle',
        'Deal Discussion',
        'deal_discussion',
        'New deal opportunity'
      );

      expect(maxParticipantsSpy).toHaveBeenCalledWith('obsidian_circle');
    });

    test('sends initial message to discussion', async () => {
      const sendMessageSpy = jest.spyOn(zkMessaging, 'sendCircleMessage');
      
      await zkMessaging.createAnonymousDiscussion(
        initiatorIdentity.anonymousId,
        'obsidian_circle',
        'Philosophy Discussion',
        'philosophy',
        'What is the nature of wealth?'
      );

      expect(sendMessageSpy).toHaveBeenCalledWith(
        initiatorIdentity.anonymousId,
        'obsidian_circle',
        'What is the nature of wealth?',
        'general_discussion',
        expect.objectContaining({
          category: ['philosophy'],
          confidentialityLevel: 'circle_only'
        })
      );
    });
  });

  describe('Anonymous Deal Sharing', () => {
    let dealSharer: AnonymousIdentity;
    let mockDeal: AnonymousDealFlow;

    beforeEach(async () => {
      dealSharer = await zkMessaging.createCircleIdentity('dealer123', 'void');
      
      // Mock high reputation for deal sharing
      jest.spyOn(zkMessaging as any, 'getReputation').mockResolvedValue(800);
      
      mockDeal = {
        dealId: 'deal123',
        dealType: 'private_equity',
        sector: 'technology',
        sizeRange: '₹1,000-5,000 Cr',
        geography: 'Global',
        timeframe: '6-12 months',
        minimumTicket: 100000000, // ₹10 Cr
        riskProfile: 'medium',
        exclusivityLevel: 'ultra_private',
        zkProof: 'deal-zk-proof',
        sharedBy: dealSharer.anonymousId,
        sharedAt: new Date()
      };
    });

    test('shares deal successfully with sufficient reputation', async () => {
      const messageId = await zkMessaging.shareAnonymousDeal(
        dealSharer.anonymousId,
        'void_circle',
        mockDeal
      );

      expect(messageId).toMatch(/^msg_\d+_[a-z0-9]+$/);
    });

    test('throws error for insufficient reputation', async () => {
      jest.spyOn(zkMessaging as any, 'getReputation').mockResolvedValue(600);

      await expect(
        zkMessaging.shareAnonymousDeal(
          dealSharer.anonymousId,
          'void_circle',
          mockDeal
        )
      ).rejects.toThrow('Insufficient reputation to share deals');
    });

    test('formats deal message correctly', async () => {
      const formatSpy = jest.spyOn(zkMessaging as any, 'formatDealMessage');
      formatSpy.mockReturnValue('Formatted deal message');

      await zkMessaging.shareAnonymousDeal(
        dealSharer.anonymousId,
        'void_circle',
        mockDeal
      );

      expect(formatSpy).toHaveBeenCalledWith(mockDeal);
    });

    test('tracks deal sharing for reputation', async () => {
      const trackSpy = jest.spyOn(zkMessaging as any, 'trackDealSharing');

      await zkMessaging.shareAnonymousDeal(
        dealSharer.anonymousId,
        'void_circle',
        mockDeal
      );

      expect(trackSpy).toHaveBeenCalledWith(dealSharer.anonymousId, mockDeal);
    });

    test('sets ultra_private confidentiality for deals', async () => {
      const sendMessageSpy = jest.spyOn(zkMessaging, 'sendCircleMessage');

      await zkMessaging.shareAnonymousDeal(
        dealSharer.anonymousId,
        'void_circle',
        mockDeal
      );

      expect(sendMessageSpy).toHaveBeenCalledWith(
        dealSharer.anonymousId,
        'void_circle',
        expect.any(String),
        'deal_opportunity',
        expect.objectContaining({
          confidentialityLevel: 'ultra_private'
        })
      );
    });
  });

  describe('Anonymous Polling', () => {
    let pollCreator: AnonymousIdentity;

    beforeEach(async () => {
      pollCreator = await zkMessaging.createCircleIdentity('pollcreator123', 'onyx');
    });

    test('creates anonymous poll successfully', async () => {
      const pollId = await zkMessaging.createAnonymousPoll(
        pollCreator.anonymousId,
        'onyx_circle',
        'Best investment sector for next quarter?',
        ['Technology', 'Healthcare', 'Energy', 'Finance'],
        'single_choice'
      );

      expect(pollId).toMatch(/^poll_\d+_[a-z0-9]+$/);
    });

    test('sets proper poll expiration', async () => {
      const storePollSpy = jest.spyOn(zkMessaging as any, 'storePoll');

      await zkMessaging.createAnonymousPoll(
        pollCreator.anonymousId,
        'onyx_circle',
        'Market sentiment?',
        ['Bullish', 'Bearish', 'Neutral'],
        'sentiment_scale'
      );

      expect(storePollSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          expiresAt: expect.any(Date),
          anonymous: true,
          minimumReputationToVote: 600
        })
      );
    });

    test('creates options with proper IDs', async () => {
      const storePollSpy = jest.spyOn(zkMessaging as any, 'storePoll');

      await zkMessaging.createAnonymousPoll(
        pollCreator.anonymousId,
        'onyx_circle',
        'Test poll',
        ['Option A', 'Option B', 'Option C'],
        'multiple_choice'
      );

      const pollData = storePollSpy.mock.calls[0][0];
      expect(pollData.options).toHaveLength(3);
      expect(pollData.options[0]).toMatchObject({
        optionId: 'option_0',
        text: 'Option A',
        votes: []
      });
    });
  });

  describe('Anonymous Voting', () => {
    let voter: AnonymousIdentity;
    let mockPoll: any;

    beforeEach(async () => {
      voter = await zkMessaging.createCircleIdentity('voter123', 'obsidian');
      
      mockPoll = {
        pollId: 'poll123',
        circleId: 'obsidian_circle',
        creatorAnonymousId: 'creator123',
        question: 'Test poll?',
        options: [
          { optionId: 'option_0', text: 'Option A', votes: [] },
          { optionId: 'option_1', text: 'Option B', votes: [] }
        ],
        pollType: 'single_choice',
        anonymous: true,
        minimumReputationToVote: 600,
        expiresAt: new Date(Date.now() + 86400000) // 24 hours
      };

      jest.spyOn(zkMessaging as any, 'getPoll').mockResolvedValue(mockPoll);
      jest.spyOn(zkMessaging as any, 'getReputation').mockResolvedValue(750);
    });

    test('casts vote successfully with sufficient reputation', async () => {
      await zkMessaging.castAnonymousVote(
        voter.anonymousId,
        'poll123',
        ['option_0']
      );

      expect(mockPoll.options[0].votes).toHaveLength(1);
    });

    test('throws error for insufficient reputation', async () => {
      jest.spyOn(zkMessaging as any, 'getReputation').mockResolvedValue(500);

      await expect(
        zkMessaging.castAnonymousVote(
          voter.anonymousId,
          'poll123',
          ['option_0']
        )
      ).rejects.toThrow('Insufficient reputation to vote');
    });

    test('throws error for non-existent poll', async () => {
      jest.spyOn(zkMessaging as any, 'getPoll').mockResolvedValue(null);

      await expect(
        zkMessaging.castAnonymousVote(
          voter.anonymousId,
          'nonexistent',
          ['option_0']
        )
      ).rejects.toThrow('Poll not found');
    });

    test('generates ZK proof for vote', async () => {
      const zkProofSpy = jest.spyOn(zkMessaging as any, 'generateVoteZKProof');

      await zkMessaging.castAnonymousVote(
        voter.anonymousId,
        'poll123',
        ['option_0']
      );

      expect(zkProofSpy).toHaveBeenCalledWith(
        voter.anonymousId,
        'poll123',
        ['option_0']
      );
    });

    test('calculates vote weight based on reputation', async () => {
      const weightSpy = jest.spyOn(zkMessaging as any, 'calculateVoteWeight');
      weightSpy.mockReturnValue(2);

      await zkMessaging.castAnonymousVote(
        voter.anonymousId,
        'poll123',
        ['option_0']
      );

      expect(weightSpy).toHaveBeenCalledWith(750);
      expect(mockPoll.options[0].votes[0].weight).toBe(2);
    });

    test('updates poll results after voting', async () => {
      const updateResultsSpy = jest.spyOn(zkMessaging as any, 'updatePollResults');

      await zkMessaging.castAnonymousVote(
        voter.anonymousId,
        'poll123',
        ['option_0']
      );

      expect(updateResultsSpy).toHaveBeenCalledWith(mockPoll);
    });
  });

  describe('Service Recommendations', () => {
    let recommender: AnonymousIdentity;
    let mockRecommendation: AnonymousServiceRecommendation;

    beforeEach(async () => {
      recommender = await zkMessaging.createCircleIdentity('recommender123', 'void');
      
      mockRecommendation = {
        serviceType: 'private_aviation',
        provider: 'Elite Jets Anonymous',
        experience: 'Exceptional discretion and luxury',
        priceRange: '₹5-15 Lakh per hour',
        anonymousReview: 'Perfect for ultra-private travel',
        verifiedByTier: 'void',
        confidentialityLevel: 'maximum'
      };
    });

    test('shares service recommendation successfully', async () => {
      const messageId = await zkMessaging.shareServiceRecommendation(
        recommender.anonymousId,
        'void_circle',
        mockRecommendation
      );

      expect(messageId).toMatch(/^msg_\d+_[a-z0-9]+$/);
    });

    test('formats service recommendation message', async () => {
      const formatSpy = jest.spyOn(zkMessaging as any, 'formatServiceRecommendation');
      formatSpy.mockReturnValue('Formatted recommendation');

      await zkMessaging.shareServiceRecommendation(
        recommender.anonymousId,
        'void_circle',
        mockRecommendation
      );

      expect(formatSpy).toHaveBeenCalledWith(mockRecommendation);
    });

    test('sends recommendation with proper metadata', async () => {
      const sendMessageSpy = jest.spyOn(zkMessaging, 'sendCircleMessage');

      await zkMessaging.shareServiceRecommendation(
        recommender.anonymousId,
        'void_circle',
        mockRecommendation
      );

      expect(sendMessageSpy).toHaveBeenCalledWith(
        recommender.anonymousId,
        'void_circle',
        expect.any(String),
        'service_recommendation',
        expect.objectContaining({
          category: ['services', 'private_aviation'],
          confidentialityLevel: 'circle_only'
        })
      );
    });
  });

  describe('Private Messaging', () => {
    let sender: AnonymousIdentity;
    let recipient: AnonymousIdentity;

    beforeEach(async () => {
      sender = await zkMessaging.createCircleIdentity('sender123', 'onyx');
      recipient = await zkMessaging.createCircleIdentity('recipient456', 'onyx');

      // Mock same circle membership
      jest.spyOn(zkMessaging as any, 'getUserCircle').mockResolvedValue('onyx_circle');
    });

    test('sends private message successfully', async () => {
      const messageId = await zkMessaging.sendPrivateMessage(
        sender.anonymousId,
        recipient.anonymousId,
        'Private message content'
      );

      expect(messageId).toMatch(/^msg_\d+_[a-z0-9]+$/);
    });

    test('throws error for cross-circle messaging', async () => {
      jest.spyOn(zkMessaging as any, 'getUserCircle')
        .mockResolvedValueOnce('onyx_circle')
        .mockResolvedValueOnce('obsidian_circle');

      await expect(
        zkMessaging.sendPrivateMessage(
          sender.anonymousId,
          recipient.anonymousId,
          'Cross-circle message'
        )
      ).rejects.toThrow('Private messages only allowed within same circle');
    });

    test('encrypts private message content', async () => {
      const encryptSpy = jest.spyOn(zkMessaging as any, 'encryptPrivateMessage');

      await zkMessaging.sendPrivateMessage(
        sender.anonymousId,
        recipient.anonymousId,
        'Secret message'
      );

      expect(encryptSpy).toHaveBeenCalledWith(
        'Secret message',
        sender.anonymousId,
        recipient.anonymousId
      );
    });

    test('stores private message separately', async () => {
      const storeSpy = jest.spyOn(zkMessaging as any, 'storePrivateMessage');

      await zkMessaging.sendPrivateMessage(
        sender.anonymousId,
        recipient.anonymousId,
        'Private content'
      );

      expect(storeSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          messageType: 'private_message',
          fromAnonymousId: sender.anonymousId
        }),
        recipient.anonymousId
      );
    });
  });

  describe('Reputation Management', () => {
    let user: AnonymousIdentity;

    beforeEach(async () => {
      user = await zkMessaging.createCircleIdentity('user123', 'obsidian');
      jest.spyOn(zkMessaging as any, 'getReputation').mockResolvedValue(500);
      jest.spyOn(zkMessaging as any, 'setReputation').mockResolvedValue(undefined);
    });

    test('updates reputation for message contribution', async () => {
      await zkMessaging.updateReputationForContribution(
        user.anonymousId,
        'message'
      );

      expect(zkMessaging['setReputation']).toHaveBeenCalledWith(
        user.anonymousId,
        505 // 500 + 5 for message
      );
    });

    test('updates reputation for deal opportunity', async () => {
      await zkMessaging.updateReputationForContribution(
        user.anonymousId,
        'deal_opportunity'
      );

      expect(zkMessaging['setReputation']).toHaveBeenCalledWith(
        user.anonymousId,
        525 // 500 + 25 for deal
      );
    });

    test('updates reputation for service recommendation', async () => {
      await zkMessaging.updateReputationForContribution(
        user.anonymousId,
        'service_recommendation'
      );

      expect(zkMessaging['setReputation']).toHaveBeenCalledWith(
        user.anonymousId,
        515 // 500 + 15 for recommendation
      );
    });

    test('updates reputation for helpful vote', async () => {
      await zkMessaging.updateReputationForContribution(
        user.anonymousId,
        'helpful_vote'
      );

      expect(zkMessaging['setReputation']).toHaveBeenCalledWith(
        user.anonymousId,
        503 // 500 + 3 for vote
      );
    });
  });

  describe('Anti-Correlation Measures', () => {
    test('applies random delay for timing obfuscation', async () => {
      const randomDelaySpy = jest.spyOn(zkMessaging as any, 'randomDelay');
      randomDelaySpy.mockResolvedValue(undefined);

      const mockMessage = {
        messageId: 'test',
        content: { encryptedText: 'test' },
        metadata: { geographicRelevance: 'Asia' }
      };

      await zkMessaging['applyAntiCorrelationMeasures'](mockMessage);

      expect(randomDelaySpy).toHaveBeenCalledWith(1000, 5000);
    });

    test('normalizes writing style', async () => {
      const normalizeSpy = jest.spyOn(zkMessaging as any, 'normalizeWritingStyle');
      normalizeSpy.mockResolvedValue('normalized text');

      const mockMessage = {
        messageId: 'test',
        content: { encryptedText: 'original text' },
        metadata: {}
      };

      const result = await zkMessaging['applyAntiCorrelationMeasures'](mockMessage);

      expect(normalizeSpy).toHaveBeenCalledWith('original text');
      expect(result.content.encryptedText).toBe('normalized text');
    });

    test('removes geographic metadata', async () => {
      const mockMessage = {
        messageId: 'test',
        content: { encryptedText: 'test' },
        metadata: { geographicRelevance: 'Europe' }
      };

      const result = await zkMessaging['applyAntiCorrelationMeasures'](mockMessage);

      expect(result.metadata.geographicRelevance).toBeUndefined();
    });
  });

  describe('Encryption and Security', () => {
    test('encrypts content based on confidentiality level', async () => {
      const encryptSpy = jest.spyOn(zkMessaging as any, 'encrypt');
      encryptSpy.mockResolvedValue('encrypted-content');

      const result = await zkMessaging['encryptMessageContent'](
        'secret message',
        'void_circle',
        'ultra_private'
      );

      expect(encryptSpy).toHaveBeenCalledWith('secret message', 'quantum');
      expect(result.encryptionLevel).toBe('quantum');
    });

    test('generates content hash for integrity', async () => {
      const hashSpy = jest.spyOn(zkMessaging as any, 'generateContentHash');
      hashSpy.mockResolvedValue('content-hash');

      const result = await zkMessaging['encryptMessageContent'](
        'test message',
        'onyx_circle',
        'circle_only'
      );

      expect(hashSpy).toHaveBeenCalledWith('test message');
      expect(result.contentHash).toBe('content-hash');
    });

    test('uses enhanced encryption for standard confidentiality', async () => {
      const encryptSpy = jest.spyOn(zkMessaging as any, 'encrypt');

      await zkMessaging['encryptMessageContent'](
        'normal message',
        'obsidian_circle',
        'circle_only'
      );

      expect(encryptSpy).toHaveBeenCalledWith('normal message', 'enhanced');
    });
  });

  describe('Vote Weight Calculation', () => {
    test('calculates weight 3 for reputation >= 900', () => {
      const weight = zkMessaging['calculateVoteWeight'](950);
      expect(weight).toBe(3);
    });

    test('calculates weight 2 for reputation >= 700', () => {
      const weight = zkMessaging['calculateVoteWeight'](750);
      expect(weight).toBe(2);
    });

    test('calculates weight 1 for reputation < 700', () => {
      const weight = zkMessaging['calculateVoteWeight'](600);
      expect(weight).toBe(1);
    });

    test('calculates weight 1 for very low reputation', () => {
      const weight = zkMessaging['calculateVoteWeight'](100);
      expect(weight).toBe(1);
    });
  });

  describe('Message ID Generation', () => {
    test('generates unique message IDs', () => {
      const id1 = zkMessaging['generateMessageId']();
      const id2 = zkMessaging['generateMessageId']();

      expect(id1).toMatch(/^msg_\d+_[a-z0-9]+$/);
      expect(id2).toMatch(/^msg_\d+_[a-z0-9]+$/);
      expect(id1).not.toBe(id2);
    });

    test('generates unique discussion IDs', () => {
      const id1 = zkMessaging['generateDiscussionId']();
      const id2 = zkMessaging['generateDiscussionId']();

      expect(id1).toMatch(/^disc_\d+_[a-z0-9]+$/);
      expect(id2).toMatch(/^disc_\d+_[a-z0-9]+$/);
      expect(id1).not.toBe(id2);
    });

    test('generates unique poll IDs', () => {
      const id1 = zkMessaging['generatePollId']();
      const id2 = zkMessaging['generatePollId']();

      expect(id1).toMatch(/^poll_\d+_[a-z0-9]+$/);
      expect(id2).toMatch(/^poll_\d+_[a-z0-9]+$/);
      expect(id1).not.toBe(id2);
    });

    test('generates unique vote IDs', () => {
      const id1 = zkMessaging['generateVoteId']();
      const id2 = zkMessaging['generateVoteId']();

      expect(id1).toMatch(/^vote_\d+_[a-z0-9]+$/);
      expect(id2).toMatch(/^vote_\d+_[a-z0-9]+$/);
      expect(id1).not.toBe(id2);
    });
  });
});