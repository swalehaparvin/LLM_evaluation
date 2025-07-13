"""
Training integration script for SafeGuardLLM adversarial datasets.
This script demonstrates how to integrate adversarial examples into training batches.
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any

def load_adversarial_dataset(filepath: str = "datasets/adv.jsonl") -> List[Dict[str, Any]]:
    """Load adversarial examples from JSONL file."""
    adversarial_examples = []
    
    with open(filepath, 'r') as f:
        for line in f:
            adversarial_examples.append(json.loads(line.strip()))
    
    return adversarial_examples

def load_main_dataset(filepath: str = "datasets/processed/combined_cybersecurity_tests.json") -> List[Dict[str, Any]]:
    """Load main cybersecurity dataset."""
    with open(filepath, 'r') as f:
        return json.load(f)

def create_mixed_batch(main_data: List[Dict], adversarial_data: List[Dict], 
                      batch_size: int = 32, adversarial_ratio: float = 0.1) -> List[Dict]:
    """
    Create a mixed training batch with adversarial examples.
    
    Args:
        main_data: Main training dataset
        adversarial_data: Adversarial examples dataset
        batch_size: Size of the training batch
        adversarial_ratio: Ratio of adversarial examples (0.05-0.1 recommended)
    
    Returns:
        Mixed training batch
    """
    # Calculate number of adversarial examples to include
    num_adversarial = int(batch_size * adversarial_ratio)
    num_main = batch_size - num_adversarial
    
    # Sample from both datasets
    main_batch = random.sample(main_data, min(num_main, len(main_data)))
    adversarial_batch = random.sample(adversarial_data, min(num_adversarial, len(adversarial_data)))
    
    # Combine and shuffle
    mixed_batch = main_batch + adversarial_batch
    random.shuffle(mixed_batch)
    
    return mixed_batch

def format_for_training(batch: List[Dict]) -> List[Dict]:
    """Format batch for training with consistent structure."""
    formatted_batch = []
    
    for item in batch:
        # Handle different data formats
        if 'prompt' in item and 'completion' in item:
            # Adversarial format
            formatted_item = {
                "input": item['prompt'],
                "output": item['completion'],
                "category": item.get('category', 'adversarial'),
                "attack_type": item.get('attack_type', 'unknown'),
                "severity": item.get('severity', 'high')
            }
        elif 'prompt' in item and 'expected_behavior' in item:
            # Main dataset format
            formatted_item = {
                "input": item['prompt'],
                "output": f"I cannot provide assistance with {item['name'].lower()}. This type of request goes against security best practices.",
                "category": item.get('category', 'cybersecurity'),
                "attack_type": item.get('name', 'unknown'),
                "severity": item.get('risk_level', 'medium')
            }
        else:
            # Skip malformed items
            continue
        
        formatted_batch.append(formatted_item)
    
    return formatted_batch

def save_training_batch(batch: List[Dict], filename: str):
    """Save formatted training batch."""
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        for item in batch:
            f.write(json.dumps(item) + '\n')
    
    print(f"Saved {len(batch)} training examples to {filepath}")

def demonstrate_training_integration():
    """Demonstrate how to integrate adversarial examples into training."""
    print("Loading datasets...")
    
    # Load datasets
    adversarial_data = load_adversarial_dataset()
    main_data = load_main_dataset()
    
    print(f"Loaded {len(adversarial_data)} adversarial examples")
    print(f"Loaded {len(main_data)} main dataset examples")
    
    # Create mixed batches with different ratios
    ratios = [0.05, 0.1, 0.15]  # 5%, 10%, 15%
    
    for ratio in ratios:
        print(f"\nCreating batch with {ratio*100}% adversarial examples...")
        
        # Create mixed batch
        mixed_batch = create_mixed_batch(main_data, adversarial_data, 
                                       batch_size=32, adversarial_ratio=ratio)
        
        # Format for training
        formatted_batch = format_for_training(mixed_batch)
        
        # Save batch
        filename = f"datasets/training_batches/batch_{int(ratio*100)}pct_adv.jsonl"
        save_training_batch(formatted_batch, filename)
        
        # Print statistics
        adversarial_count = sum(1 for item in formatted_batch if item['category'] == 'adversarial')
        main_count = len(formatted_batch) - adversarial_count
        
        print(f"  Batch composition: {main_count} main + {adversarial_count} adversarial = {len(formatted_batch)} total")
        print(f"  Actual ratio: {adversarial_count/len(formatted_batch)*100:.1f}%")

def create_safeguard_training_config():
    """Create training configuration for SafeGuardLLM."""
    config = {
        "training_strategy": "adversarial_robustness",
        "adversarial_ratio": 0.1,
        "batch_size": 32,
        "epochs": 3,
        "learning_rate": 2e-5,
        "safety_guidelines": {
            "refuse_system_disclosure": True,
            "refuse_credential_extraction": True,
            "maintain_role_boundaries": True,
            "resist_social_engineering": True,
            "detect_advanced_attacks": True
        },
        "evaluation_metrics": [
            "refusal_rate",
            "safety_boundary_maintenance",
            "attack_detection_accuracy",
            "response_consistency"
        ]
    }
    
    with open("datasets/training_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print("Created training configuration: datasets/training_config.json")

if __name__ == "__main__":
    print("SafeGuardLLM Adversarial Training Integration")
    print("=" * 50)
    
    try:
        demonstrate_training_integration()
        create_safeguard_training_config()
        
        print("\n" + "=" * 50)
        print("Training Integration Complete!")
        print("\nRecommendations:")
        print("1. Use 5-10% adversarial examples in each training batch")
        print("2. Monitor refusal rates during training")
        print("3. Evaluate safety boundaries after each epoch")
        print("4. Test with held-out adversarial examples")
        print("5. Ensure consistent refusal responses across attack types")
        
    except Exception as e:
        print(f"Error during integration: {e}")
        import traceback
        traceback.print_exc()