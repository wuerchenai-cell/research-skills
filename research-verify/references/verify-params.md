# Verify: Parameters

## Purpose

Check datasheet parameters, tolerances, and constraints.

## Workflow

1. Extract the parameter, value, unit, and tolerance from the original source.
2. Check the value against stated constraints and operating conditions.
3. Flag values that depend on temperature, voltage, frequency, or process.
4. Mark unverified parameters.

## Quality gates

- Every parameter has value, unit, and source.
- Tolerances and conditions are stated.
- Unverified parameters are marked.

## Common pitfalls

- Copying a parameter without its conditions.
- Mixing min/typ/max values.
