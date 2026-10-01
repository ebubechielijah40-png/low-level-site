"""Shared bounds and structured results; never executes user source as host code."""
import time

class RunError(Exception):
    pass

class Budget:
    def __init__(self, limit=12000):
        self.limit = limit
        self.steps = 0
        self.started = time.monotonic()
        self.trace = []
        self.output = ''
    def tick(self, detail=None):
        self.steps += 1
        if self.steps > self.limit or time.monotonic() - self.started > 1.5:
            raise RunError('Execution limit reached. Check for an infinite loop or reduce the work.')
        if detail and len(self.trace) < 200:
            self.trace.append(detail)
    def emit(self, s):
        s = str(s)
        if len(self.output) + len(s) > 16000:
            raise RunError('Output limit reached (16,000 characters).')
        self.output += s


def validate_source(code):
    if not isinstance(code, str) or not code.strip():
        raise RunError('Write a program before running it.')
    if len(code.encode('utf-8')) > 24000:
        raise RunError('Source limit is 24 KB.')
    # Limits parsing depth even for intentionally adversarial inputs.
    depth = 0
    for ch in code:
        if ch in '([{': depth += 1
        if ch in ')]}': depth = max(0, depth-1)
        if depth > 60: raise RunError('Nesting limit is 60 levels.')


def result(budget, engine, state=None, errors=None, **extra):
    return dict(output=budget.output, errors=errors or [], trace=budget.trace,
                steps=budget.steps, engine=engine, state=state or {}, **extra)
