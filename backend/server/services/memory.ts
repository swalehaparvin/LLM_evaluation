// server/services/memory.ts
// Enhanced memory service with proper TypeScript implementation

export interface ThreatMemory {
  id?: string;
  threat_type: string;
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  context: string;
  timestamp: string;
  session_id: string;
  user_id?: string;
}

interface MemoryStore {
  [userId: string]: ThreatMemory[];
}

interface MemorySearchResult {
  memory: string;
  metadata: ThreatMemory;
  score?: number;
}

// Enhanced in-memory storage implementation
class MemoryService {
  private memoryStore: MemoryStore = {};
  private memoryIdCounter = 0;

  constructor() {
    // Initialize with some default memory data for testing
    this.initializeDefaultMemories();
  }

  private initializeDefaultMemories() {
    // Add some default threat memories for testing
    const defaultUserId = "default";
    this.memoryStore[defaultUserId] = [
      {
        id: `mem-${++this.memoryIdCounter}`,
        threat_type: "SQL Injection",
        description: "Detected SQL injection attempt in user input",
        severity: "high",
        context: "User attempted to inject SQL commands through login form",
        timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
        session_id: "session-default-1",
        user_id: defaultUserId,
      },
      {
        id: `mem-${++this.memoryIdCounter}`,
        threat_type: "XSS Attack",
        description: "Cross-site scripting vulnerability found",
        severity: "medium",
        context: "Script tags detected in user comment section",
        timestamp: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
        session_id: "session-default-2",
        user_id: defaultUserId,
      },
    ];
  }

  async add(data: any, options: { user_id: string }): Promise<ThreatMemory> {
    const userId = options.user_id || "default";

    if (!this.memoryStore[userId]) {
      this.memoryStore[userId] = [];
    }

    const threat: ThreatMemory = {
      id: `mem-${++this.memoryIdCounter}`,
      threat_type: data.metadata?.threat_type || "Unknown",
      description: data.messages?.[0]?.content || data.description || "",
      severity: data.metadata?.severity || "medium",
      context: data.messages?.[1]?.content || data.context || "",
      timestamp: data.metadata?.timestamp || new Date().toISOString(),
      session_id: data.metadata?.session_id || `session-${Date.now()}`,
      user_id: userId,
    };

    this.memoryStore[userId].push(threat);
    return threat;
  }

  async search(
    query: string,
    options: { user_id: string; limit?: number },
  ): Promise<MemorySearchResult[]> {
    const userId = options.user_id || "default";
    const limit = options.limit || 10;
    const userThreats = this.memoryStore[userId] || [];

    if (!query) {
      // Return all threats if no query
      return userThreats.slice(0, limit).map((threat) => ({
        memory: `${threat.threat_type}: ${threat.description}`,
        metadata: threat,
        score: 1.0,
      }));
    }

    const lowerQuery = query.toLowerCase();

    // Score and filter threats based on relevance
    const scoredThreats = userThreats
      .map((threat) => {
        let score = 0;
        const lowerDesc = threat.description.toLowerCase();
        const lowerType = threat.threat_type.toLowerCase();
        const lowerContext = threat.context.toLowerCase();

        // Exact matches get higher scores
        if (lowerDesc.includes(lowerQuery)) score += 0.5;
        if (lowerType.includes(lowerQuery)) score += 0.3;
        if (lowerContext.includes(lowerQuery)) score += 0.2;

        // Keyword matches
        const queryWords = lowerQuery.split(" ");
        queryWords.forEach((word) => {
          if (lowerDesc.includes(word)) score += 0.1;
          if (lowerType.includes(word)) score += 0.1;
        });

        return { threat, score };
      })
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);

    return scoredThreats.map((item) => ({
      memory: `${item.threat.threat_type}: ${item.threat.description}`,
      metadata: item.threat,
      score: item.score,
    }));
  }

  async get_all(options: { user_id: string }): Promise<ThreatMemory[]> {
    const userId = options.user_id || "default";
    return this.memoryStore[userId] || [];
  }

  async update(
    memoryId: string,
    data: Partial<ThreatMemory>,
  ): Promise<boolean> {
    for (const userId in this.memoryStore) {
      const threats = this.memoryStore[userId];
      const index = threats.findIndex((t) => t.id === memoryId);

      if (index !== -1) {
        threats[index] = { ...threats[index], ...data };
        return true;
      }
    }
    return false;
  }

  async delete(memoryId: string): Promise<boolean> {
    for (const userId in this.memoryStore) {
      const threats = this.memoryStore[userId];
      const index = threats.findIndex((t) => t.id === memoryId);

      if (index !== -1) {
        threats.splice(index, 1);
        return true;
      }
    }
    return false;
  }

  // Get all users who have threat memories
  async getAllUsers(): Promise<string[]> {
    return Object.keys(this.memoryStore);
  }

  // Clear all memories for a user
  async clearUserMemories(userId: string): Promise<void> {
    delete this.memoryStore[userId];
  }
}

// Create singleton instance
const memory = new MemoryService();

export class GeminiMemoryService {
  private memory: MemoryService;

  constructor() {
    this.memory = memory;
  }

  // Store threat information in long-term memory
  async storeThreat(
    threat: ThreatMemory,
    userId: string,
  ): Promise<ThreatMemory> {
    try {
      const memoryData = {
        messages: [
          {
            role: "user",
            content: `Threat detected: ${threat.threat_type} - ${threat.description}`,
          },
          {
            role: "assistant",
            content: `Recorded threat of severity ${threat.severity} with context: ${threat.context}`,
          },
        ],
        metadata: {
          threat_type: threat.threat_type,
          severity: threat.severity,
          timestamp: threat.timestamp,
          session_id: threat.session_id,
        },
        description: threat.description,
        context: threat.context,
      };

      const storedThreat = await this.memory.add(memoryData, {
        user_id: userId,
      });
      return storedThreat;
    } catch (error) {
      console.error("Error storing threat in memory:", error);
      throw error;
    }
  }

  // Retrieve relevant threat history for context
  async getRelevantThreats(
    query: string,
    userId: string,
  ): Promise<MemorySearchResult[]> {
    try {
      const results = await this.memory.search(query, {
        user_id: userId,
        limit: 10,
      });
      return results;
    } catch (error) {
      console.error("Error retrieving threat history:", error);
      return [];
    }
  }

  // Get all threats for a user
  async getUserThreatHistory(userId: string): Promise<ThreatMemory[]> {
    try {
      const results = await this.memory.get_all({ user_id: userId });
      return results;
    } catch (error) {
      console.error("Error retrieving user threat history:", error);
      return [];
    }
  }

  // Update threat information
  async updateThreat(
    memoryId: string,
    updatedData: Partial<ThreatMemory>,
  ): Promise<boolean> {
    try {
      const success = await this.memory.update(memoryId, updatedData);
      return success;
    } catch (error) {
      console.error("Error updating threat memory:", error);
      throw error;
    }
  }

  // Delete threat from memory
  async deleteThreat(memoryId: string): Promise<boolean> {
    try {
      const success = await this.memory.delete(memoryId);
      return success;
    } catch (error) {
      console.error("Error deleting threat memory:", error);
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
      const threatContext = relevantThreats
        .slice(0, 5) // Limit to top 5 most relevant
        .map((result) => {
          const threat = result.metadata;
          return `• Previous ${threat.severity} severity ${threat.threat_type}: ${threat.description}`;
        })
        .join("\n");

      // Enhanced prompt with threat history context
      const enhancedPrompt = `Based on previous security evaluations:
${threatContext}

Current evaluation request:
${prompt}

Please provide a comprehensive security evaluation considering the historical context above.`;

      return enhancedPrompt;
    } catch (error) {
      console.error("Error building enhanced context:", error);
      return prompt;
    }
  }

  // Get statistics about stored threats
  async getThreatStatistics(userId?: string): Promise<any> {
    try {
      const threats = userId
        ? await this.memory.get_all({ user_id: userId })
        : Object.values(this.memory["memoryStore"] as MemoryStore).flat();

      const stats = {
        total: threats.length,
        bySeverity: {
          critical: threats.filter((t) => t.severity === "critical").length,
          high: threats.filter((t) => t.severity === "high").length,
          medium: threats.filter((t) => t.severity === "medium").length,
          low: threats.filter((t) => t.severity === "low").length,
        },
        byType: threats.reduce(
          (acc, threat) => {
            acc[threat.threat_type] = (acc[threat.threat_type] || 0) + 1;
            return acc;
          },
          {} as Record<string, number>,
        ),
        recentThreats: threats
          .sort(
            (a, b) =>
              new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
          )
          .slice(0, 5),
      };

      return stats;
    } catch (error) {
      console.error("Error getting threat statistics:", error);
      return null;
    }
  }
}

export const memoryService = new GeminiMemoryService();
