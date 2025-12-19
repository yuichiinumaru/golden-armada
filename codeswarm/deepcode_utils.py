import re
import logging

logger = logging.getLogger(__name__)

def assess_output_completeness(text: str) -> float:
    """
    Assess the completeness of the YAML output plan.

    Based on DeepCode's _assess_output_completeness.

    Returns:
        float: Completeness score (0.0-1.0)
    """
    if not text or len(text.strip()) < 500:
        return 0.0

    score = 0.0
    text_lower = text.lower()

    # 1. Check for required 5 sections
    required_sections = [
        "file_structure:",
        "implementation_components:",
        "validation_approach:",
        "environment_setup:",
        "implementation_strategy:",
    ]

    sections_found = sum(1 for section in required_sections if section in text_lower)
    section_score = sections_found / len(required_sections)
    score += section_score * 0.5

    # 2. Check for YAML structure
    has_yaml_start = any(
        marker in text
        for marker in ["```yaml", "complete_reproduction_plan:", "paper_info:"]
    )
    has_yaml_end = any(
        marker in text[-500:]
        for marker in ["```", "implementation_strategy:", "validation_approach:"]
    )

    if has_yaml_start and has_yaml_end:
        score += 0.2
    elif has_yaml_start:
        score += 0.1

    # 3. Check last line integrity
    lines = text.strip().split("\n")
    if lines:
        last_line = lines[-1].strip()
        if (
            last_line.endswith(("```", ".", ":", "]", "}"))
            or last_line.startswith(("-", "*", " "))
            or (len(last_line) < 100 and not last_line.endswith(","))
        ):
            score += 0.15

    # 4. Check length
    length = len(text)
    if length >= 10000:
        score += 0.15
    elif length >= 5000:
        score += 0.10
    elif length >= 2000:
        score += 0.05

    return min(score, 1.0)

from typing import Optional

def extract_file_tree_from_plan(plan_content: str) -> Optional[str]:
    """
    Extract file tree structure from initial_plan.txt content.

    Based on DeepCode's extract_file_tree_from_plan.
    """
    # Look for file structure section, specifically "## File Structure" format
    file_structure_pattern = r"## File Structure[^\n]*\n```[^\n]*\n(.*?)\n```"

    match = re.search(file_structure_pattern, plan_content, re.DOTALL)
    if match:
        file_tree = match.group(1).strip()
        lines = file_tree.split("\n")

        # Clean tree structure
        cleaned_lines = []
        for line in lines:
            if line.strip() and (
                any(char in line for char in ["├──", "└──", "│"])
                or line.strip().endswith("/")
                or "." in line.split("/")[-1]
                or line.strip().endswith(".py")
                or line.strip().endswith(".txt")
                or line.strip().endswith(".md")
                or line.strip().endswith(".yaml")
            ):
                cleaned_lines.append(line)

        if len(cleaned_lines) >= 5:
            return "\n".join(cleaned_lines)

    # Fallback: look for any code block containing project structure
    code_block_patterns = [
        r"```[^\n]*\n(project/.*?(?:├──|└──).*?)\n```",
        r"```[^\n]*\n(src/.*?(?:├──|└──).*?)\n```",
        r"```[^\n]*\n(core/.*?(?:├──|└──).*?)\n```",
        r"```[^\n]*\n(.*?(?:├──|└──).*?(?:\.py|\.txt|\.md|\.yaml).*?)\n```",
    ]

    for pattern in code_block_patterns:
        match = re.search(pattern, plan_content, re.DOTALL)
        if match:
            file_tree = match.group(1).strip()
            lines = [line for line in file_tree.split("\n") if line.strip()]
            if len(lines) >= 5:
                return file_tree

    # Final fallback: extract file paths from file mentions
    file_mentions = re.findall(
        r"`([^`]*(?:\.py|\.txt|\.md|\.yaml|\.yml)[^`]*)`", plan_content
    )

    if file_mentions:
        dirs = set()
        files_by_dir = {}

        for file_path in file_mentions:
            file_path = file_path.strip()
            if "/" in file_path:
                dir_path = "/".join(file_path.split("/")[:-1])
                filename = file_path.split("/")[-1]
                dirs.add(dir_path)
                if dir_path not in files_by_dir:
                    files_by_dir[dir_path] = []
                files_by_dir[dir_path].append(filename)
            else:
                if "root" not in files_by_dir:
                    files_by_dir["root"] = []
                files_by_dir["root"].append(file_path)

        structure_lines = []

        # Determine root directory name
        if any("src/" in f for f in file_mentions):
            root_name = "src"
        elif any("core/" in f for f in file_mentions):
            root_name = "core"
        elif any("lib/" in f for f in file_mentions):
            root_name = "lib"
        else:
            root_name = "project"
        structure_lines.append(f"{root_name}/")

        sorted_dirs = sorted(dirs) if dirs else []
        for i, dir_path in enumerate(sorted_dirs):
            is_last_dir = i == len(sorted_dirs) - 1
            prefix = "└──" if is_last_dir else "├──"
            structure_lines.append(f"{prefix} {dir_path}/")

            if dir_path in files_by_dir:
                files = sorted(files_by_dir[dir_path])
                for j, filename in enumerate(files):
                    is_last_file = j == len(files) - 1
                    if is_last_dir:
                        file_prefix = "    └──" if is_last_file else "    ├──"
                    else:
                        file_prefix = "│   └──" if is_last_file else "│   ├──"
                    structure_lines.append(f"{file_prefix} {filename}")

        if "root" in files_by_dir:
            root_files = sorted(files_by_dir["root"])
            for i, filename in enumerate(root_files):
                is_last = (i == len(root_files) - 1) and not sorted_dirs
                prefix = "└──" if is_last else "├──"
                structure_lines.append(f"{prefix} {filename}")

        if len(structure_lines) >= 3:
            return "\n".join(structure_lines)

    return None
