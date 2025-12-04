#!/usr/bin/env tsx
/**
 * Test script for Regional Guardrails with Arabic reviews sample
 * Tests real-world Arabic content for safety validation
 */

import { regionalGuardrails } from './services/regional-guardrails';
import * as fs from 'fs';

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
};

interface Review {
  text: string;
}

interface TestResult {
  id: number;
  preview: string;
  status: string;
  violations: string[];
  reason?: string;
  confidence: number;
  duration: number;
  redacted?: boolean;
}

async function testArabicReviews() {
  console.log(`\n${colors.bright}${colors.cyan}📝 ARABIC REVIEWS REGIONAL GUARDRAILS TEST${colors.reset}`);
  console.log(`${colors.cyan}${'='.repeat(60)}${colors.reset}\n`);
  
  // Check if OpenAI API key is configured
  if (!process.env.OPENAI_API_KEY) {
    console.error(`${colors.red}❌ Error: OPENAI_API_KEY not configured${colors.reset}`);
    console.log('Please set your OpenAI API key in the environment variables');
    return;
  }

  // Load the Arabic reviews
  let reviews: Review[];
  const SAMPLE_SIZE = 30; // Test a representative sample
  try {
    const data = fs.readFileSync('../arabic_reviews_sample.json', 'utf8');
    const allReviews: Review[] = JSON.parse(data);
    // Take a random sample for testing
    reviews = allReviews
      .sort(() => Math.random() - 0.5)
      .slice(0, SAMPLE_SIZE);
    console.log(`${colors.green}✅ Loaded ${allReviews.length} Arabic reviews, testing ${SAMPLE_SIZE} random samples${colors.reset}\n`);
  } catch (error) {
    console.error(`${colors.red}❌ Failed to load arabic_reviews_sample.json: ${error}${colors.reset}`);
    return;
  }

  const results: TestResult[] = [];
  let allowed = 0;
  let blocked = 0;
  let redacted = 0;
  let errors = 0;

  // Test each review
  for (let i = 0; i < reviews.length; i++) {
    const review = reviews[i];
    const preview = review.text.substring(0, 60) + (review.text.length > 60 ? '...' : '');
    
    console.log(`${colors.bright}[Review ${i + 1}/${reviews.length}]${colors.reset}`);
    console.log(`${colors.cyan}Text:${colors.reset} "${preview}"`);
    
    try {
      const startTime = Date.now();
      const result = await regionalGuardrails.evaluate(review.text);
      const duration = Date.now() - startTime;
      
      // Determine status icon
      let statusIcon = '';
      switch (result.status) {
        case 'ALLOW':
          statusIcon = `${colors.green}✅ SAFE${colors.reset}`;
          allowed++;
          break;
        case 'BLOCK':
          statusIcon = `${colors.red}🚫 BLOCKED${colors.reset}`;
          blocked++;
          break;
        case 'REDACTED':
          statusIcon = `${colors.yellow}🔒 REDACTED${colors.reset}`;
          redacted++;
          break;
        default:
          statusIcon = `${colors.magenta}⚠️ ${result.status}${colors.reset}`;
      }
      
      console.log(`${colors.magenta}Status:${colors.reset} ${statusIcon}`);
      
      if (result.violations && result.violations.length > 0) {
        console.log(`${colors.yellow}Violations:${colors.reset} ${result.violations.join(', ')}`);
      }
      
      if (result.reason) {
        console.log(`${colors.blue}Reason:${colors.reset} ${result.reason}`);
      }
      
      console.log(`${colors.blue}Response Time:${colors.reset} ${duration}ms | ${colors.cyan}Confidence:${colors.reset} ${((result.confidence || 0) * 100).toFixed(0)}%`);
      
      results.push({
        id: i + 1,
        preview,
        status: result.status,
        violations: result.violations || [],
        reason: result.reason,
        confidence: result.confidence || 0,
        duration,
        redacted: result.status === 'REDACTED'
      });
      
    } catch (error) {
      console.log(`${colors.red}❌ ERROR${colors.reset} - ${error instanceof Error ? error.message : 'Unknown error'}`);
      errors++;
      
      results.push({
        id: i + 1,
        preview,
        status: 'ERROR',
        violations: [],
        confidence: 0,
        duration: 0
      });
    }
    
    console.log('');
  }
  
  // Summary
  console.log(`${colors.cyan}${'='.repeat(60)}${colors.reset}`);
  console.log(`${colors.bright}📊 ARABIC REVIEWS TEST SUMMARY${colors.reset}`);
  console.log(`${colors.cyan}${'='.repeat(60)}${colors.reset}`);
  console.log(`Total Reviews Tested: ${colors.bright}${reviews.length}${colors.reset}`);
  console.log(`${colors.green}✅ Safe (ALLOW):${colors.reset} ${allowed} (${((allowed/reviews.length)*100).toFixed(1)}%)`);
  console.log(`${colors.red}🚫 Blocked:${colors.reset} ${blocked} (${((blocked/reviews.length)*100).toFixed(1)}%)`);
  console.log(`${colors.yellow}🔒 Redacted:${colors.reset} ${redacted} (${((redacted/reviews.length)*100).toFixed(1)}%)`);
  if (errors > 0) {
    console.log(`${colors.red}❌ Errors:${colors.reset} ${errors}`);
  }
  
  // Collect all violations found
  const allViolations = results
    .flatMap(r => r.violations)
    .filter(v => v && v.length > 0);
  
  if (allViolations.length > 0) {
    const violationCounts: Record<string, number> = {};
    allViolations.forEach(v => {
      violationCounts[v] = (violationCounts[v] || 0) + 1;
    });
    
    console.log(`\n${colors.bright}Violations Found:${colors.reset}`);
    Object.entries(violationCounts)
      .sort((a, b) => b[1] - a[1])
      .forEach(([violation, count]) => {
        console.log(`  ${colors.yellow}${violation}:${colors.reset} ${count}`);
      });
  }
  
  // Performance stats
  const avgDuration = results
    .filter(r => r.duration > 0)
    .reduce((sum, r) => sum + r.duration, 0) / results.filter(r => r.duration > 0).length;
  
  console.log(`\n${colors.bright}Performance:${colors.reset}`);
  console.log(`Average Response Time: ${colors.yellow}${avgDuration.toFixed(0)}ms${colors.reset}`);
  
  // Save results
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const resultsFile = `arabic_reviews_test_${timestamp}.json`;
  
  try {
    await fs.promises.writeFile(
      resultsFile,
      JSON.stringify({
        timestamp: new Date().toISOString(),
        source: 'arabic_reviews_sample.json',
        summary: {
          total: reviews.length,
          allowed,
          blocked,
          redacted,
          errors,
          safeRate: ((allowed/reviews.length)*100).toFixed(1) + '%',
          avgResponseTime: avgDuration.toFixed(0) + 'ms'
        },
        results
      }, null, 2)
    );
    console.log(`\n${colors.green}✅ Results saved to ${resultsFile}${colors.reset}`);
  } catch (error) {
    console.error(`${colors.red}Failed to save results: ${error}${colors.reset}`);
  }
  
  console.log(`\n${colors.bright}${colors.cyan}🛡️ Arabic reviews test complete!${colors.reset}\n`);
}

// Run tests if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  testArabicReviews().catch(console.error);
}