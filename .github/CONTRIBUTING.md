# Contributing to AI-Hackathon-Judge

Thank you for your interest in contributing to **AI-Hackathon-Judge** 🎉  
We welcome contributions that improve functionality, security, documentation, and overall project quality.

This document explains how you can contribute effectively and responsibly.

---

## 📌 Ways to Contribute

You can help the project in many ways, including:

- 🐞 Reporting bugs
- ✨ Suggesting or implementing new features
- 🧠 Improving AI evaluation or scoring logic
- 📄 Enhancing documentation
- 🛡️ Strengthening security practices
- 🧪 Adding or improving tests

---

## 🧾 Before You Start

- Please search existing **Issues** and **Pull Requests** to avoid duplicates.
- For security-related issues, **do NOT open a public issue**.  
  Follow the instructions in [`SECURITY.md`](SECURITY.md).

---

## 🛠️ Development Setup

1. **Fork** the repository.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/AI-Hackathon-Judge.git
   cd AI-Hackathon-Judge
   ```
3. Create a new branch for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Install dependencies as described in `../README.md`.
    - *Tip: You can use `docker-compose up --build` to skip manual dependency installation.*
5. Configure environment variables and API keys securely.

---

## 🧪 Testing & Code Quality

- Ensure your changes do not break existing functionality.
- Add tests where applicable.
- Run linters or formatters if configured.
- Do not commit debug logs, secrets, or temporary files.

---

## 📝 Commit Message Guidelines

Use clear and descriptive commit messages.

**Format:**
```
type: short description
```

**Examples:**
- `feat: add AI evaluation explanation module`
- `fix: handle empty repository input`
- `docs: update setup instructions`
- `security: improve prompt injection safeguards`

---

## 🔁 Pull Request Process

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Open a **Pull Request** against the `main` branch.
3. In the PR description, include:
   - What problem the PR solves
   - Summary of changes
   - Screenshots or demo links (if applicable)
4. Ensure your PR:
   - Is focused and minimal
   - Passes all checks
   - Does not introduce security risks

---

## 🔐 Security & Responsible Disclosure

- Never include API keys, tokens, or credentials in commits.
- Avoid exposing sensitive system or environment details.
- Follow the responsible disclosure process in [`SECURITY.md`](SECURITY.md).

---

## 🧠 AI & Ethics Guidelines

Since this project involves AI and LLMs:

- Avoid introducing biased, unsafe, or misleading AI behavior.
- Be careful with prompt construction and user-controlled inputs.
- Prefer transparency and explainability in AI outputs.

---

## 🏁 Final Notes

- All contributions are reviewed for quality, clarity, and alignment with project goals.
- Maintainers may request changes before merging.
- All contributions are subject to the project license.

Thank you for contributing to **AI-Hackathon-Judge** 🚀
