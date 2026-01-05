"""
Structured prompt templates for LLM-based PII leak verification.

Contains multiple prompt versions for A/B testing and optimization.
"""
from app.prompts.few_shot_examples import get_formatted_examples


# Version 1: Basic Zero-Shot Prompt (Current/Baseline)
BASIC_PROMPT_V1 = """You are a Privacy Security Auditor. Your job is to find any UNREDACTED
Personally Identifiable Information (PII) in the text below.

PII includes: Names, Emails, SSNs, Phone Numbers, or ID numbers.

Text to check: "{text}"

Return ONLY a JSON object with:
"leaked": true/false,
"reason": "explanation of what was missed"
"""


# Version 2: Chain-of-Thought Reasoning
CHAIN_OF_THOUGHT_PROMPT_V2 = """You are a Privacy Security Auditor analyzing redacted text for PII leaks.

## Task
Identify ANY unredacted Personally Identifiable Information (PII) in the text below.

## PII Categories to Check
- Names (full names, first names with last initial, nicknames)
- Email addresses
- Phone numbers (any format: (555) 123-4567, 555-123-4567, +1-555-123-4567)
- Social Security Numbers (SSNs, any format)
- Physical addresses
- ID numbers (employee IDs, customer IDs, account numbers, license plates)
- Dates of birth
- Medical record numbers
- IP addresses
- Partial identifiers (last 4 of SSN, partial credit card, etc.)

## Analysis Process (Think Step-by-Step)

**Text to analyze:**
"{text}"

**Your Analysis:**
1. **Scan for names:** Look for proper nouns, titles (Dr., Mr., Mrs.), and personal names
2. **Check emails:** Look for name@domain.com patterns
3. **Find phone numbers:** Check for digit patterns that match phone formats
4. **Identify numbers:** Look for SSNs, IDs, account numbers
5. **Check addresses:** Look for street addresses, zip codes
6. **Verify redaction tokens:** Ensure [REDACTED_xxxx] tokens are used for sensitive data

**Decision:**
Are there any PII values that are NOT redacted (not replaced with [REDACTED_xxxx] tokens)?

## Output Format
Return ONLY valid JSON:
{{"leaked": true/false, "reason": "specific explanation of what leaked or why it's clean"}}
"""


# Version 3: Few-Shot Learning (Best Performance)
def get_few_shot_prompt_v3(text: str, num_examples: int = 3) -> str:
    """
    Generate few-shot prompt with examples.

    Args:
        text: Text to analyze
        num_examples: Number of few-shot examples to include

    Returns:
        Formatted prompt with examples
    """
    examples = get_formatted_examples(count=num_examples, include_analysis=True)

    return f"""You are a Privacy Security Auditor specialized in detecting PII leaks in redacted text.

## Your Task
Analyze text to find ANY unredacted Personally Identifiable Information (PII).
Properly redacted text uses tokens like [REDACTED_xxxx].

## PII Types
- Names, Emails, Phone Numbers, SSNs, Addresses, IDs, Dates of Birth, Medical Records, IP Addresses

## Examples of Correct Analysis

{examples}

## Now Analyze This Text

Text: "{text}"

Think through each PII category systematically. Are there any identifiers that are NOT redacted?

Return ONLY valid JSON:
{{"leaked": true/false, "reason": "specific explanation"}}
"""


# Version 4: Optimized Few-Shot (Concise)
def get_optimized_few_shot_prompt_v4(text: str) -> str:
    """
    Optimized few-shot prompt (shorter, faster inference).

    Args:
        text: Text to analyze

    Returns:
        Optimized prompt
    """
    # Use only 2 best examples (leaked + clean)
    return f"""You are a PII leak detector. Find unredacted PII (names, emails, phones, SSNs, IDs).

Examples:
- "[REDACTED_a1] at [REDACTED_b2]" → {{"leaked": false, "reason": "All PII redacted"}}
- "Email john@test.com" → {{"leaked": true, "reason": "Email john@test.com exposed"}}
- "Call 555-1234" → {{"leaked": true, "reason": "Phone 555-1234 exposed"}}

Text: "{text}"

JSON only:"""


def get_prompt(version: str, text: str, **kwargs) -> str:
    """
    Get prompt by version.

    Args:
        version: Prompt version (v1_basic, v2_cot, v3_few_shot, v4_optimized)
        text: Text to analyze
        **kwargs: Additional parameters (e.g., num_examples for few-shot)

    Returns:
        Formatted prompt string
    """
    if version == "v1_basic":
        return BASIC_PROMPT_V1.format(text=text)
    elif version == "v2_cot":
        return CHAIN_OF_THOUGHT_PROMPT_V2.format(text=text)
    elif version == "v3_few_shot":
        num_examples = kwargs.get("num_examples", 3)
        return get_few_shot_prompt_v3(text, num_examples)
    elif version == "v4_optimized":
        return get_optimized_few_shot_prompt_v4(text)
    else:
        # Default to basic
        return BASIC_PROMPT_V1.format(text=text)


if __name__ == "__main__":
    # Test prompts
    test_text = "Contact [REDACTED_a1b2] at john.doe@example.com"

    print("=" * 70)
    print("PROMPT VERSION COMPARISON")
    print("=" * 70)
    print()

    for version in ["v1_basic", "v2_cot", "v3_few_shot", "v4_optimized"]:
        print(f"### {version.upper()} ###")
        print()
        prompt = get_prompt(version, test_text)
        print(prompt)
        print()
        print("-" * 70)
        print()
