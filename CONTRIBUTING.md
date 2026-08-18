# Contributing to Ethical Exploration

Thank you for your interest in contributing to **Ethical Exploration**! We welcome contributions from developers, security researchers, and enthusiasts of all skill levels.

By participating in this project, you agree to uphold our ethical standards and abide by the guidelines set forth in this document.

---

## Table of Contents

1. [Ethical Standards & Responsible Disclosure](#ethical-standards--responsible-disclosure)
2. [Code of Conduct](#code-of-conduct)
3. [How Can I Contribute?](#how-can-i-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Suggesting Enhancements](#suggesting-enhancements)
   - [Contributing Code](#contributing-code)
4. [Development Workflow](#development-workflow)
   - [Git Branching Strategy](#git-branching-strategy)
   - [Code Quality & Standards](#code-quality--standards)
   - [Testing Your Changes](#testing-your-changes)
5. [Pull Request Process](#pull-request-process)
6. [Licensing](#licensing)

---

## Ethical Standards & Responsible Disclosure

Ethical Exploration is developed strictly for **educational, defensive, and authorized penetration testing purposes**.

- **Authorization First**: Never test security tools against networks, systems, or web applications without explicit, written authorization from the system owner.
- **No Malicious Intent**: Tools and scripts must not include unauthenticated backdoors, malicious droppers, unconstrained ransomware payloads, or non-educational malware.
- **Responsible Disclosure**: If you discover a vulnerability in an external service or this codebase, follow responsible disclosure practices by notifying maintainers privately before publicizing.

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for all contributors. Please ensure that all communications across discussions, issues, and pull requests remain constructive, respectful, and professional.

---

## How Can I Contribute?

### Reporting Bugs

Before submitting an issue, please search existing issues to ensure the bug has not already been reported. When submitting a bug report, include:
- **Clear Title**: Brief summary of the bug.
- **Environment**: Operating System, Python/.NET/Bash/Node version.
- **Steps to Reproduce**: Detailed commands and input data that trigger the issue.
- **Expected vs. Actual Behavior**: What should have happened vs. what actually occurred.
- **Logs/Screenshots**: Relevant error tracebacks or console outputs (masking any private IPs or credentials).

### Suggesting Enhancements

Enhancement suggestions are encouraged! Please open an issue with:
- A descriptive title.
- The use case and rationale for the proposed feature.
- Example CLI interface, function signature, or intended workflow.

### Contributing Code

We welcome contributions across all supported languages:
- **Python**: Network scanners, web security tools, automation scripts, parsers.
- **C#**: .NET utilities, reconnaissance modules, Windows API integrations.
- **Shell / Bash**: Linux automation, socket probing, system auditing.
- **Batch / PowerShell**: Windows administrative scripts, optimization, audit tools.
- **JavaScript / PHP**: Web exploit proof-of-concepts, test handlers, audit payloads.

---

## Development Workflow

### Git Branching Strategy

1. **Fork or clone** the repository:
   ```bash
   git clone https://github.com/sanguirIS/Ethical_Exploration.git
   cd Ethical_Exploration
   ```
2. **Create a topic branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit changes** with clear, atomic commit messages:
   ```bash
   git commit -m "feat(scanner): add support for multi-target CIDR notation"
   ```

### Code Quality & Standards

- **Python**: Follow [PEP 8](https://peps.python.org/pep-0008/). Use type hints where appropriate. Include `argparse` with `--help` descriptions and examples.
- **C#**: Follow standard .NET naming conventions (PascalCase for public methods/classes, camelCase for local variables). Ensure clean exception handling.
- **Shell / Bash**: Ensure scripts run cleanly in `/bin/bash` with defensive quoting around variables (`"$VAR"`).
- **Documentation**: All public functions and scripts must include docstrings or header comments detailing their purpose, arguments, and usage examples.

### Testing Your Changes

Before submitting a pull request, verify that all modified scripts compile and run cleanly:
```bash
# Verify Python scripts syntax
python3 -m py_compile *.py

# Verify JavaScript syntax
node -c *.js

# Test tools against local mock servers or safe endpoints
python3 HashCracker.py -H 5f4dcc3b5aa765d61d8327deb882cf99 -w sample_wordlists/passwords.txt
python3 portScan.py -t 127.0.0.1 -p 22,80,443
```

---

## Pull Request Process

1. Ensure the working directory is clean and all tests pass.
2. Update `README.md` documentation if introducing new tools, parameters, or flags.
3. Submit a Pull Request targeting the default branch.
4. Describe the changes in detail within the PR description, referencing any associated issue numbers (e.g., `Closes #12`).
5. Maintainers will review the PR, request any necessary adjustments, and merge once approved.

---

## Licensing

By contributing to Ethical Exploration, you agree that your contributions will be licensed under the **GNU General Public License v3.0 (GPL-3.0)**.
