from typing import Dict, Any, Optional


from src.utils.str_utils import lowercase_first_char, format_to_str


def build_prompt_from_config(
        config: Dict[str, str|list[str]],
        input_data: str = "",
        app_config: Optional[Dict[str, Any]] = None,
) -> str:
    """Builds a complete prompt string based on a config dictionary.

    Args:
        config: Dictionary specifying prompt components.
        input_data: Content to be summarized or processed.
        app_config: Optional app-wide configuration (e.g., reasoning strategies).

    Returns:
        A fully constructed prompt as a string.

    Raises:
        ValueError: If the required 'instruction' field is missing.
    """
    prompt_parts = []

    if role := config.get("role"):
        prompt_parts.append(f"You are {lowercase_first_char(role.strip())}.")

    instruction = config.get("instruction")
    if not instruction:
        raise ValueError("Missing required field: 'instruction'")
    prompt_parts.append(format_to_str("Your task is as follows:", instruction))

    if context := config.get("context"):
        prompt_parts.append(f"Here’s some background that may help you:\n{context}")

    if constraints := config.get("output_constraints"):
        prompt_parts.append(
            format_to_str(
                "Ensure your response follows these rules:", constraints
            )
        )

    if tone := config.get("style_or_tone"):
        prompt_parts.append(
            format_to_str(
                "Follow these style and tone guidelines in your response:", tone
            )
        )

    if format_ := config.get("output_format"):
        prompt_parts.append(
            format_to_str("Structure your response as follows:", format_)
        )

    if examples := config.get("examples"):
        prompt_parts.append(format_to_str("Here are some examples to guide your response:", examples))
        if isinstance(examples, list):
            for idx, example in enumerate(examples, 1):
                prompt_parts.append(f"Example {idx}:\n{example}")
        else:
            prompt_parts.append(f"Example:\n{str(examples)}")

    if goal := config.get("goal"):
        prompt_parts.append(format_to_str("Keep this overall goal in mind as you work on the task:", goal))

    if input_data:
        prompt_parts.append(
            "Here is the input data you should work with:\n<<<BEGING CONTENT>>>\n"
            f"```\n{input_data.strip()}\n```\n<<<END CONTENT>>>"
        )

    reasoning_strategy = config.get("reasoning_strategy")
    if reasoning_strategy and reasoning_strategy != "None" and app_config:
        strategies = app_config.get("reasoning_strategies", {})
        if strategy_text := strategies.get(reasoning_strategy):
            prompt_parts.append(strategy_text.strip())

    prompt_parts.append("Please provide your response based on the above instructions and information.")
    return "\n\n".join(prompt_parts)

