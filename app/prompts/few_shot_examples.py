"""
Curated few-shot examples for LLM prompt engineering.

These examples teach the LLM to detect PII leaks in redacted text.
"""

# Few-shot examples for leak detection
FEW_SHOT_EXAMPLES = [
    {
        "text": "Contact [REDACTED_a1b2] at [REDACTED_c3d4] for more information.",
        "analysis": "Scanning for PII: No email addresses, phone numbers, or names visible. All sensitive information replaced with redaction tokens.",
        "leaked": False,
        "reason": "All PII properly redacted with placeholder tokens"
    },
    {
        "text": "Email john.doe@example.com for details",
        "analysis": "Found unredacted email address 'john.doe@example.com' which is personally identifiable information.",
        "leaked": True,
        "reason": "Email address john.doe@example.com not redacted"
    },
    {
        "text": "Employee ID EMP-12345 belongs to [REDACTED_xyz9]",
        "analysis": "Found employee identifier 'EMP-12345' which can be used to identify an individual. Name is properly redacted.",
        "leaked": True,
        "reason": "Employee identifier EMP-12345 leaked"
    },
    {
        "text": "The patient was treated by Dr. [REDACTED_m5n6] at [REDACTED_p7q8]",
        "analysis": "All names and locations are properly redacted. Only generic terms 'patient' and 'Dr.' remain, which are not PII.",
        "leaked": False,
        "reason": "All identifiable information redacted, only generic roles mentioned"
    },
    {
        "text": "Call 555-1234 to reach [REDACTED_k2l3]",
        "analysis": "Phone number '555-1234' is exposed and not redacted. This is personally identifiable contact information.",
        "leaked": True,
        "reason": "Phone number 555-1234 exposed"
    },
    {
        "text": "[REDACTED_b4c5] lives at [REDACTED_d6e7], [REDACTED_f8g9]",
        "analysis": "Name and address components all properly redacted with tokens. No identifiable information visible.",
        "leaked": False,
        "reason": "Complete redaction of name and address"
    },
    {
        "text": "SSN ending in 6789",
        "analysis": "Partial SSN '6789' is revealed. While not a complete SSN, last 4 digits can still be identifying information.",
        "leaked": True,
        "reason": "Partial SSN (last 4 digits: 6789) leaked"
    },
]


def get_few_shot_examples(count: int = 3) -> list:
    """
    Get a subset of few-shot examples.

    Args:
        count: Number of examples to return

    Returns:
        List of example dictionaries
    """
    return FEW_SHOT_EXAMPLES[:count]


def format_example_for_prompt(example: dict, include_analysis: bool = True) -> str:
    """
    Format a single example for inclusion in prompt.

    Args:
        example: Example dictionary
        include_analysis: Whether to include step-by-step analysis

    Returns:
        Formatted example string
    """
    result = f'Text: "{example["text"]}"\n'

    if include_analysis:
        result += f'Analysis: {example["analysis"]}\n'

    result += f'Result: {{"leaked": {"true" if example["leaked"] else "false"}, "reason": "{example["reason"]}"}}'

    return result


def get_formatted_examples(count: int = 3, include_analysis: bool = True) -> str:
    """
    Get formatted examples for prompt.

    Args:
        count: Number of examples
        include_analysis: Include step-by-step analysis

    Returns:
        Formatted examples as string
    """
    examples = get_few_shot_examples(count)
    formatted = []

    for i, example in enumerate(examples, 1):
        formatted.append(f"Example {i}:\n{format_example_for_prompt(example, include_analysis)}")

    return "\n\n".join(formatted)


if __name__ == "__main__":
    # Test example formatting
    print("=== Few-Shot Examples ===\n")
    print(get_formatted_examples(count=3, include_analysis=True))
