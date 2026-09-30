# Local Python app first, shared server later

The tool is a Python application that runs on the engineer's own PC, with its input form opening in the browser. The long-term goal is a single copy on a firm server that other engineers use through a URL. We start local because there is one user today and a server needs IT, uptime and sign-in work that buys nothing yet. Python was chosen over a browser-only TypeScript app so the engineer of record can read the check code, which reads close to a hand calc. The calc engine must stay independent of the form, so moving to the server changes only the front end and how the tool is deployed, never the calc.

## Considered Options

- Browser-only TypeScript app: no install for colleagues, but the code is harder for the engineer of record to review, and polished PDF output is more limited.
- Shared server from day one: the eventual target, but premature with one user.
- Notebook or spreadsheet: inputs and formulas stay editable by whoever has the file open, which rules it out as a controlled tool.
