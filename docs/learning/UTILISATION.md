# Core utilisation harness

The schedule expands one stimulus into its model/sample/repeat requests. Each
response is saved before measurement and later evaluated in separate Windows
workers. The monitor counts completed records and estimates remaining generation
time. Read studies/utilisation/HARNESS.md for files and commands.

1. Why can a lost response cause two server attempts but one scored row?
2. What independent count must match the Ollama response?
3. Why is a capped response distinguished from a truncated prompt?
4. Which windows contribute to net post-load CPU energy?
5. Why can a benchmark reference fail the polynomial-root oracle?

Assumptions: frozen stimulus text includes all separators and the independent
token counts include the server template. The CSV clock and format are correct.
Task IDs and options in frozen materials are audited. Cache counter semantics
require verification on the actual Ollama version. Tests use a mocked server.
