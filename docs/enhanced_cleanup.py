import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
import difflib
from collections import defaultdict

class DocumentationCleaner:
    def __init__(self):
        # Patterns for navigation and redundant elements
        self.patterns = {
            'nav_menu': re.compile(
                r'Get Started\n(?:[\w\s]+\n)*API Reference\n(?:Contribute ❤️\n)?',
                re.MULTILINE
            ),
            'toc': re.compile(
                r'Table of contents\n(?:\s*[-*]\s*.*?\n)+',
                re.MULTILINE
            ),
            'file_header': re.compile(
                r'^--- START OF FILE .*?---\n|^Title: .*?\n',
                re.MULTILINE
            ),
            'next_prev': re.compile(
                r'\n(Previous|Next)\n.*?(?=\n\w|$)',
                re.MULTILINE | re.DOTALL
            ),
            'code_block': re.compile(
                r'```(python|java|json|yaml|bash|shell)\n\s*',
                re.MULTILINE
            ),
            'empty_lines': re.compile(r'\n{3,}', re.MULTILINE)
        }
        
        # Common redundant sections to remove
        self.redundant_sections = [
            'Table of contents',
            'Next steps',
            'Back to top',
            'Copyright',
            'Made with Material for MkDocs',
            'Skip to content',
            'Community Resources',
            'Contributing Guide'
        ]

    def clean_content(self, content: str) -> str:
        """Apply all cleaning patterns to the content."""
        # Remove navigation elements
        for pattern in self.patterns.values():
            content = pattern.sub('', content)
        
        # Remove redundant sections
        for section in self.redundant_sections:
            content = re.sub(
                f'\n*{re.escape(section)}\n+[-=]*\n*',
                '\n',
                content,
                flags=re.IGNORECASE
            )
        
        # Clean up headers
        content = self._clean_headers(content)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        content = self.patterns['empty_lines'].sub('\n\n', content)
        
        return content.strip()
    
    def _clean_headers(self, content: str) -> str:
        """Clean and normalize markdown headers."""
        # Convert === and --- headers to # headers
        content = re.sub(
            r'^([^\n]+)\n=+\n',
            r'# \1\n\n',
            content,
            flags=re.MULTILINE
        )
        content = re.sub(
            r'^([^\n]+)\n-+\n',
            r'## \1\n\n',
            content,
            flags=re.MULTILINE
        )
        
        # Remove duplicate headers
        seen_headers = set()
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.startswith('#'):
                header = line.strip(' #').lower()
                if header in seen_headers:
                    continue
                seen_headers.add(header)
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def find_duplicate_sections(self, content: str) -> Dict[str, List[Tuple[int, int]]]:
        """Find potentially duplicate sections in the content."""
        sections = defaultdict(list)
        
        # Extract all sections with their content
        section_pattern = re.compile(
            r'^(#{1,6})\s+(.*?)(?=\n(?:^#|\Z))',
            re.MULTILINE | re.DOTALL
        )
        
        for match in section_pattern.finditer(content):
            level = len(match.group(1))
            title = match.group(2).strip()
            section_content = match.group(0).strip()
            
            # Skip very short sections
            if len(section_content) < 100:
                continue
                
            sections[title.lower()].append((title, section_content))
        
        # Filter for duplicates
        return {
            title: sections_list
            for title, sections_list in sections.items()
            if len(sections_list) > 1
        }

def main():
    input_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'adk-a2a-documentation-cleaned.md'
    )
    output_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'adk-a2a-documentation-enhanced.md'
    )
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Please run the initial cleanup script first.")
        return
    
    print(f"Loading and cleaning documentation from '{input_file}'...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cleaner = DocumentationCleaner()
    
    # Find and report duplicate sections
    print("\nAnalyzing content for duplicate sections...")
    duplicates = cleaner.find_duplicate_sections(content)
    
    if duplicates:
        print("\nFound potential duplicate sections:")
        for title, sections in duplicates.items():
            print(f"\n- {sections[0][0]} (found {len(sections)} times)")
    else:
        print("No significant duplicate sections found.")
    
    # Clean the content
    print("\nCleaning content...")
    cleaned_content = cleaner.clean_content(content)
    
    # Write the cleaned content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    # Report statistics
    original_size = len(content)
    new_size = len(cleaned_content)
    reduction = (1 - (new_size / original_size)) * 100
    
    print("\nCleaning complete!")
    print(f"Original size: {original_size} characters")
    print(f"Cleaned size:  {new_size} characters")
    print(f"Reduction:     {reduction:.1f}%")
    print(f"\nCleaned documentation saved to: {output_file}")
    
    if duplicates:
        print("\nNote: The following sections were identified as potential duplicates.")
        print("Please review and consolidate these sections manually:")
        for title, sections in duplicates.items():
            print(f"- {sections[0][0]} (found {len(sections)} times)")

if __name__ == "__main__":
    main()
