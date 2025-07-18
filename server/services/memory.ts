// Note: mem0ai is a Python package, creating a TypeScript wrapper
// We'll implement a simple in-memory threat storage for now
interface MemoryStore {
  [userId: string]: ThreatMemory[];
}

// Simple in-memory storage for threats (replace with proper database in production)
const memoryStore: MemoryStore = {};

// Mock Memory class to simulate mem0ai functionality
class MockMemory {
  async add(data: any, options: { user_id: string }) {
    if (!memoryStore[options.user_id]) {
      memoryStore[options.user_id] = [];
    }
    
    const threat: ThreatMemory = {
      threat_type: data.metadata?.threat_type || "Unknown",
      description: data.messages[0]?.content || "",
      severity: data.metadata?.severity || "medium",
      context: data.messages[1]?.content || "",
      timestamp: data.metadata?.timestamp || new Date().toISOString(),
      session_id: data.metadata?.session_id || `session-${Date.now()}`
    };
    
    memoryStore[options.user_id].push(threat);
  }

  async search(query: string, options: { user_id: string; limit: number }) {
    const userThreats = memoryStore[options.user_id] || [];
    const lowerQuery = query.toLowerCase();
    
    return userThreats
      .filter(threat => 
        threat.description.toLowerCase().includes(lowerQuery) ||
        threat.threat_type.toLowerCase().includes(lowerQuery) ||
        threat.context.toLowerCase().includes(lowerQuery)
      )
      .slice(0, options.limit)
      .map(threat => ({
        memory: threat.description,
        metadata: threat
      }));
  }

  async get_all(options: { user_id: string }) {
    return memoryStore[options.user_id] || [];
  }

  async update(memoryId: string, data: any) {
    // Simple implementation for updating
    console.log('Memory update not implemented in mock');
  }

  async delete(memoryId: string) {
    // Simple implementation for deleting
    console.log('Memory delete not implemented in mock');
  }
}

const memory = new MockMemory();

export interface ThreatMemory {
  threat_type: string;
  description: string;
  severity: string;
  context: string;
  timestamp: string;
  session_id: string;
}

export class GeminiMemoryService {
  private memory: any;
  
  constructor() {
    this.memory = memory;
  }

  // Store threat information in long-term memory
  async storeThreat(threat: ThreatMemory, userId: string): Promise<void> {
    try {
      const memoryData = {
        messages: [
          {
            role: "user",
            content: `Threat detected: ${threat.threat_type} - ${threat.description}`
          },
          {
            role: "assistant", 
            content: `Recorded threat of severity ${threat.severity} with context: ${threat.context}`
          }
        ],
        metadata: {
          threat_type: threat.threat_type,
          severity: threat.severity,
          timestamp: threat.timestamp,
          session_id: threat.session_id
        }
      };

      await this.memory.add(memoryData, { user_id: userId });
    } catch (error) {
      console.error('Error storing threat in memory:', error);
      throw error;
    }
  }

  // Retrieve relevant threat history for context
  async getRelevantThreats(query: string, userId: string): Promise<any[]> {
    try {
      const results = await this.memory.search(query, { user_id: userId, limit: 10 });
      return results;
    } catch (error) {
      console.error('Error retrieving threat history:', error);
      return [];
    }
  }

  // Get all threats for a user
  async getUserThreatHistory(userId: string): Promise<any[]> {
    try {
      const results = await this.memory.get_all({ user_id: userId });
      return results;
    } catch (error) {
      console.error('Error retrieving user threat history:', error);
      return [];
    }
  }

  // Update threat information
  async updateThreat(memoryId: string, updatedData: any): Promise<void> {
    try {
      await this.memory.update(memoryId, updatedData);
    } catch (error) {
      console.error('Error updating threat memory:', error);
      throw error;
    }
  }

  // Delete threat from memory
  async deleteThreat(memoryId: string): Promise<void> {
    try {
      await this.memory.delete(memoryId);
    } catch (error) {
      console.error('Error deleting threat memory:', error);
      throw error;
    }
  }

  // Get enhanced context for Gemini evaluation
  async getEnhancedContext(prompt: string, userId: string): Promise<string> {
    try {
      const relevantThreats = await this.getRelevantThreats(prompt, userId);
      
      if (relevantThreats.length === 0) {
        return prompt;
      }

      // Build context from previous threats
      const threatContext = relevantThreats.map(threat => {
        const metadata = threat.metadata || {};
        return `Previous threat: ${metadata.threat_type || 'Unknown'} (${metadata.severity || 'Unknown'} severity) - ${threat.memory || threat.content}`;
      }).join('\n');

      // Enhanced prompt with threat history context
      const enhancedPrompt = `
Context from previous security evaluations:
${threatContext}

Current evaluation prompt:
${prompt}

Based on the threat history above, provide a comprehensive security evaluation.`;

      return enhancedPrompt;
    } catch (error) {
      console.error('Error building enhanced context:', error);
      return prompt;
    }
  }
}

export const memoryService = new GeminiMemoryService();