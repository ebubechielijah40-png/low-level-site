import re


def _evaluate_c_variables(code: str):
    variables = {}
    for raw_line in code.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('//'):
            continue

        declaration = re.match(r'int\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\d+)\s*;', line)
        if declaration:
            variables[declaration.group(1)] = int(declaration.group(2))
            continue

        assignment = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*([+\-*/])\s*(\d+)\s*;', line)
        if assignment:
            name = assignment.group(1)
            lhs = variables.get(assignment.group(2), 0)
            value = int(assignment.group(4))
            operator = assignment.group(3)
            if operator == '+':
                variables[name] = lhs + value
            elif operator == '-':
                variables[name] = lhs - value
            elif operator == '*':
                variables[name] = lhs * value
            elif operator == '/':
                variables[name] = lhs // value if value else 0
            continue

        assignment_value = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\d+)\s*;', line)
        if assignment_value:
            variables[assignment_value.group(1)] = int(assignment_value.group(2))

    return variables


def analyze_c_code(code: str):
    errors = []
    output = []

    if 'int main()' not in code:
        errors.append('Missing main() function. Define an entry point.')

    if 'return 0;' not in code:
        errors.append('Missing return 0; at the end of main().')

    variables = _evaluate_c_variables(code)
    if 'printf' in code:
        printf_match = re.search(r'printf\s*\(\s*"([^"]*)"', code)
        if printf_match:
            fmt = printf_match.group(1).replace('\\n', '\n')
            if '%d' in fmt:
                if variables:
                    output.append(str(next(iter(variables.values()))))
                else:
                    output.append('0')
            else:
                output.append(fmt)

    if not errors:
        output_text = ''.join(output).strip()
        if output_text:
            return {'output': output_text, 'errors': [], 'trace': ['printf emitted output']}

        return {'output': 'Program executed. No output was produced.', 'errors': [], 'trace': ['Program executed']}

    return {'output': '', 'errors': errors, 'trace': ['Static analysis detected issues']}


def analyze_assembly_code(code: str):
    errors = []
    output_lines = []

    if 'mov' not in code.lower() and 'add' not in code.lower() and 'sub' not in code.lower():
        errors.append('Add a basic MOV, ADD, or SUB instruction to begin.')

    if 'rax' in code.lower():
        output_lines.append('rax register updated')

    if not errors:
        return {'output': ' | '.join(output_lines) or 'Assembly instructions parsed.', 'errors': [], 'trace': ['Assembly parsed']}

    return {'output': '', 'errors': errors, 'trace': ['Assembly parsing failed']}
