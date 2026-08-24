from django.test import SimpleTestCase

from core.code_runner import analyze_assembly_code, analyze_c_code


class CodeRunnerTests(SimpleTestCase):
    def test_c_code_missing_return_is_reported(self):
        result = analyze_c_code('#include <stdio.h>\nint main() {\n    printf("hi");\n}')
        self.assertTrue(any('return 0' in error.lower() for error in result['errors']))

    def test_valid_c_code_returns_output(self):
        result = analyze_c_code('#include <stdio.h>\nint main() {\n    int x = 3;\n    x = x + 2;\n    printf("%d\\n", x);\n    return 0;\n}')
        self.assertEqual(result['output'], '5')

    def test_assembly_code_reports_register_value(self):
        result = analyze_assembly_code('mov rax, 2\nadd rax, 3')
        self.assertIn('rax', result['output'])
