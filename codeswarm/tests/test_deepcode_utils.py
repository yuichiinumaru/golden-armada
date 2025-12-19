import unittest
from codeswarm.deepcode_utils import assess_output_completeness, extract_file_tree_from_plan

class TestDeepCodeUtils(unittest.TestCase):
    def test_assess_output_completeness_empty(self):
        self.assertEqual(assess_output_completeness(""), 0.0)
        self.assertEqual(assess_output_completeness("short"), 0.0)

    def test_assess_output_completeness_partial(self):
        # Create a text longer than 500 chars with meaningful content
        content_filler = "This is some filler content to ensure the text length exceeds the minimum threshold of 500 characters required by the assessment function. " * 10
        text = f"""
{content_filler}
```yaml
complete_reproduction_plan:
  paper_info:
    title: "Test Paper"
  file_structure: |
    project/
    ├── main.py
  implementation_components: |
    Component 1
```
"""
        # Should be > 0 but < 1.0.
        # Has sections (2/5), yaml markers (partial).
        score = assess_output_completeness(text)
        self.assertTrue(score > 0.0, f"Score {score} should be > 0.0")
        self.assertTrue(score < 1.0, f"Score {score} should be < 1.0")

    def test_extract_file_tree_from_plan_structure_block(self):
        plan = """
## File Structure
```
project/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
├── requirements.txt
└── README.md
```
"""
        tree = extract_file_tree_from_plan(plan)
        self.assertIsNotNone(tree)
        self.assertIn("project/", tree)
        self.assertIn("main.py", tree)

    def test_extract_file_tree_from_mentions(self):
        plan = """
We need to create `src/main.py` and `src/utils.py`.
Also `tests/test_main.py` is important.
Don't forget `requirements.txt`.
"""
        tree = extract_file_tree_from_plan(plan)
        self.assertIsNotNone(tree)
        self.assertIn("src/", tree)
        self.assertIn("main.py", tree)

if __name__ == '__main__':
    unittest.main()
