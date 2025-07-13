import fs from 'fs';
import path from 'path';
import { db } from './db';
import { testSuites, testCases } from '@shared/schema';

interface NewDatasetTestCase {
  id: string;
  name: string;
  description: string;
  category: string;
  prompt: string;
  system_prompt: string;
  expected_behavior: string;
  risk_level: string;
  metadata: {
    techniques?: string[];
    threat_type?: string;
    attack_type?: string;
    test_type?: string;
  };
}

async function loadNewCybersecurityDatasets() {
  console.log("Loading new cybersecurity datasets...");

  try {
    // Load the combined cybersecurity test cases
    const datasetsPath = path.join(process.cwd(), 'datasets/processed/combined_cybersecurity_tests.json');
    
    if (!fs.existsSync(datasetsPath)) {
      console.log("No new datasets found. Please run the dataset integration script first.");
      return;
    }

    const newTestCases: NewDatasetTestCase[] = JSON.parse(
      fs.readFileSync(datasetsPath, 'utf8')
    );

    console.log(`Found ${newTestCases.length} new test cases`);

    // Create new test suites for the datasets
    const newTestSuites = [
      {
        name: "CTI Threat Intelligence",
        description: "Cybersecurity Threat Intelligence evaluation tests focusing on threat actor techniques and attack patterns",
        category: "threat_intelligence",
        severity: "high",
        isActive: true
      },
      {
        name: "Adversarial Robustness",
        description: "Tests for adversarial attacks including prompt injection, system prompt extraction, and safety bypasses",
        category: "adversarial_robustness",
        severity: "critical",
        isActive: true
      },
      {
        name: "MISP Attack Patterns",
        description: "MISP Galaxy attack pattern database tests for comprehensive threat modeling",
        category: "misp_patterns",
        severity: "high",
        isActive: true
      }
    ];

    // Insert new test suites
    const insertedSuites = await db.insert(testSuites).values(newTestSuites).returning();
    console.log(`✅ Created ${insertedSuites.length} new test suites`);

    // Map test cases to appropriate test suites
    const suiteMap = new Map<string, number>();
    for (const suite of insertedSuites) {
      if (suite.category === "threat_intelligence") {
        suiteMap.set("cti_threat_intelligence", suite.id);
      } else if (suite.category === "adversarial_robustness") {
        suiteMap.set("adversarial_robustness", suite.id);
      } else if (suite.category === "misp_patterns") {
        suiteMap.set("misp_attack_pattern", suite.id);
      }
    }

    // Process and insert test cases
    const testCaseInserts = [];
    let processedCount = 0;

    for (const testCase of newTestCases) {
      const testSuiteId = suiteMap.get(testCase.category);
      
      if (testSuiteId) {
        // Map risk level to severity
        const severityMap: Record<string, string> = {
          "critical": "critical",
          "high": "high",
          "medium": "medium",
          "low": "low"
        };

        const testCaseData = {
          testSuiteId,
          testId: testCase.id,
          name: testCase.name,
          description: testCase.description,
          prompt: testCase.prompt,
          systemPrompt: testCase.system_prompt,
          expectedOutcome: testCase.expected_behavior,
          evaluationCriteria: {
            original_id: testCase.id,
            category: testCase.category,
            risk_level: testCase.risk_level,
            expected_behavior: testCase.expected_behavior,
            ...testCase.metadata
          }
        };

        testCaseInserts.push(testCaseData);
        processedCount++;
      }
    }

    // Insert test cases in batches
    if (testCaseInserts.length > 0) {
      const insertedTestCases = await db.insert(testCases).values(testCaseInserts).returning();
      console.log(`✅ Created ${insertedTestCases.length} new test cases`);
    }

    // Print summary
    console.log(`\n🎉 New cybersecurity datasets loaded successfully!`);
    console.log(`📊 Summary:
    - New Test Suites: ${insertedSuites.length}
    - New Test Cases: ${processedCount}
    - CTI Threat Intelligence: ${newTestCases.filter(tc => tc.category === "cti_threat_intelligence").length}
    - Adversarial Robustness: ${newTestCases.filter(tc => tc.category === "adversarial_robustness").length}
    - MISP Attack Patterns: ${newTestCases.filter(tc => tc.category === "misp_attack_pattern").length}
    `);

    return {
      suites: insertedSuites.length,
      testCases: processedCount,
      categories: {
        cti: newTestCases.filter(tc => tc.category === "cti_threat_intelligence").length,
        adversarial: newTestCases.filter(tc => tc.category === "adversarial_robustness").length,
        misp: newTestCases.filter(tc => tc.category === "misp_attack_pattern").length
      }
    };

  } catch (error) {
    console.error("❌ Error loading new cybersecurity datasets:", error);
    throw error;
  }
}

// Run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  loadNewCybersecurityDatasets().then((result) => {
    console.log("✅ New dataset loading complete!");
    if (result) {
      console.log(`📈 Total additions: ${result.suites} suites, ${result.testCases} test cases`);
    }
    process.exit(0);
  }).catch((error) => {
    console.error("❌ New dataset loading failed:", error);
    process.exit(1);
  });
}

export { loadNewCybersecurityDatasets };