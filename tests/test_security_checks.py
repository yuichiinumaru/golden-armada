import unittest
import os
import tempfile
import shutil
from pathlib import Path # Not strictly needed for this test logic, but good practice for path manipulation in general

class TestPathSafetyChecks(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory that will serve as target_project_path
        self.target_project_path_obj = tempfile.TemporaryDirectory(prefix="sec_check_")
        self.target_project_path = os.path.abspath(self.target_project_path_obj.name)
        # print(f"setUp: target_project_path = {self.target_project_path}")

    def tearDown(self):
        # Clean up the temporary directory
        self.target_project_path_obj.cleanup()
        # print(f"tearDown: cleaned up {self.target_project_path}")

    def test_path_validation_logic(self):
        # This test simulates the core logic for ensuring resolved paths stay within a designated project directory.
        # The `target_project_path` is the root directory where operations are allowed.
        # `relative_path_input` simulates a path (e.g., from LLM output) that is meant to be relative to target_project_path.

        # Note on os.path.join behavior with absolute paths:
        # If `relative_path_input` is an absolute path (e.g., "/etc/passwd"),
        # os.path.join(base, absolute_path) will return `absolute_path`.
        # The safety check `startswith(os.path.abspath(target_project_path))`
        # should then correctly evaluate if this absolute path is within the project.

        test_cases = [
            # Valid cases (should be safe)
            ("Valid relative path", "file.txt", True),
            ("Valid relative path with subdirectory", "subdir/file.txt", True),
            ("Valid path with dot", "./file.txt", True),
            ("Valid path with parent and child dirs, normalized", "subdir/../subdir/file.txt", True),
            ("Empty relative path", "", True), # os.path.join(base, "") returns base
            ("Path is just a dot", ".", True), # os.path.join(base, ".") returns base
            ("Path with trailing slash", "subdir/", True),
            ("Path with multiple slashes", "subdir///file.txt", True),

            # Invalid cases (should be unsafe - path traversal attempts)
            ("Path traversal attempt (single parent)", "../file_outside.txt", False),
            ("Path traversal attempt (multiple parents)", "../../file_further_outside.txt", False),
            ("Path traversal with valid subdir then parent", "subdir/../../file_outside_root.txt", False),

            # Absolute paths (should be unsafe if not within target_project_path)
            # On POSIX, os.path.join("/a/b", "/c/d") yields "/c/d".
            # The safety check should then compare if "/c/d" starts with "/a/b".
            ("Absolute path input - POSIX root", "/etc/passwd", False),
            ("Absolute path input - Windows style C drive", "C:\\Windows\\System32\\calc.exe", False),

            # Cases that might look like traversal but normalize to be safe
            ("Path with redundant parent and current dirs, but safe", "subdir/./../file_in_root.txt", True), # Normalizes to file_in_root.txt
            ("Path that normalizes to target_project_path itself", "subdir/..", True), # Normalizes to target_project_path

            # A tricky case: if target_project_path is part of a longer path that is then traversed upwards
            # e.g. target_project_path = /tmp/test/project
            # input = ../project_sibling/file.txt -> /tmp/test/project_sibling/file.txt (unsafe)
            # This is covered by the basic ".." checks.
        ]

        # Create a dummy file/dir inside target_project_path to ensure normalization works as expected for some cases
        os.makedirs(os.path.join(self.target_project_path, "subdir"), exist_ok=True)
        with open(os.path.join(self.target_project_path, "file_in_root.txt"), "w") as f:
            f.write("dummy")

        for description, relative_path_input, expected_is_safe in test_cases:
            with self.subTest(description=description, input_path=relative_path_input):
                # 1. Construct the path as it might be done in application code
                # os.path.normpath is important to resolve ".." and "."
                constructed_path = os.path.normpath(os.path.join(self.target_project_path, relative_path_input))

                # 2. The safety check itself:
                # Ensure both paths are absolute and normalized for a reliable string comparison.
                # os.path.abspath will also normalize the path.
                abs_constructed_path = os.path.abspath(constructed_path)
                abs_target_project_path = os.path.abspath(self.target_project_path)

                # The core security check: Does the resolved absolute path of the file/directory
                # start with the resolved absolute path of the allowed project directory?
                # We also need to ensure that if they are the same, it's considered safe.
                # And if the constructed path is a subdirectory, it must also have a separator.

                # Heuristic to detect Windows-style absolute paths, which os.path.join
                # on POSIX systems would incorrectly treat as relative.
                is_win_abs_path = len(relative_path_input) > 2 and relative_path_input[1] == ':' and relative_path_input[0].isalpha()

                is_safe = False
                # Only run the startswith check if it's not a cross-platform absolute path issue.
                if not (is_win_abs_path and os.name != 'nt'):
                    if abs_constructed_path == abs_target_project_path:
                        is_safe = True
                    elif abs_constructed_path.startswith(abs_target_project_path + os.sep):
                        is_safe = True

                # Debug print for diagnostics if a test fails
                # print(
                #     f"\nDesc: {description}\n"
                #     f"Input: '{relative_path_input}'\n"
                #     f"Target: '{abs_target_project_path}'\n"
                #     f"Constructed (abs): '{abs_constructed_path}'\n"
                #     f"Expected safe: {expected_is_safe}, Actual safe: {is_safe}"
                # )

                self.assertEqual(is_safe, expected_is_safe, msg=f"{description} - Input: '{relative_path_input}'")

    def test_edge_case_target_path_symlink(self):
        # This is a more advanced scenario. If target_project_path itself is a symlink,
        # os.path.abspath resolves it. The check should still be against the resolved path.
        # For simplicity, this test assumes os.path.abspath correctly handles symlinks,
        # which is standard OS behavior. The logic itself doesn't need to change.
        # True setup of symlinks is OS-dependent and might require permissions.

        original_target_dir = os.path.join(self.target_project_path, "original_data")
        os.makedirs(original_target_dir)

        symlink_path = os.path.join(self.target_project_path_obj.name, "project_symlink")

        # Skip symlink test on Windows if not admin or dev mode, as it often fails
        if os.name == 'nt':
            try:
                os.symlink(original_target_dir, symlink_path, target_is_directory=True)
            except OSError:
                self.skipTest("Symlink creation failed on Windows (possibly due to permissions/dev mode). Skipping symlink test.")
                return
        else:
             os.symlink(original_target_dir, symlink_path, target_is_directory=True)


        abs_symlink_path = os.path.abspath(symlink_path) # This resolves to where original_target_dir is

        # Path relative to the symlink that is valid
        relative_to_symlink_valid = "file_in_symlinked_dir.txt"
        constructed_valid = os.path.normpath(os.path.join(symlink_path, relative_to_symlink_valid))
        abs_constructed_valid = os.path.abspath(constructed_valid)

        is_safe_valid = False
        if abs_constructed_valid == abs_symlink_path or abs_constructed_valid.startswith(abs_symlink_path + os.sep):
             is_safe_valid = True
        self.assertTrue(is_safe_valid, "Path within a symlinked target_project_path should be safe relative to the symlink's resolved path.")

        # Path relative to symlink that tries to escape the symlink's target
        relative_to_symlink_invalid = "../file_outside_symlink_target.txt"
        constructed_invalid = os.path.normpath(os.path.join(symlink_path, relative_to_symlink_invalid))
        abs_constructed_invalid = os.path.abspath(constructed_invalid)

        is_safe_invalid = False
        if abs_constructed_invalid == abs_symlink_path or abs_constructed_invalid.startswith(abs_symlink_path + os.sep):
            is_safe_invalid = True
        self.assertFalse(is_safe_invalid, "Path escaping a symlinked target_project_path should be unsafe relative to the symlink's resolved path.")

        if os.path.islink(symlink_path) or os.path.exists(symlink_path): # cleanup, islink for POSIX, exists for junctions on win
            if os.name == 'nt':
                if os.path.isdir(symlink_path): # Junctions are removed with rmdir
                    os.rmdir(symlink_path)
            else: # Regular symlinks
                os.unlink(symlink_path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
