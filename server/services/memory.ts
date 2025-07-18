import mem0ai from 'mem0ai';

// Initialize Memory with Gemini configuration
const memory = mem0ai.Memory.from_config({
  llm: {
    provider: "gemini",
    config: {
      model: "gemini-2.5-flash",
      temperature: 0,
      api_key: process.env.GEMINI_API_KEY
    }
  },
  embedder: {
    provider: "gemini",
    config: {
      model: "text-embedding-004",
      api_key: process.env.GEMINI_API_KEY
    }
  }
});

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