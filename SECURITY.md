# Security Policy for AI-Hackathon-Judge

## 🚨 Reporting a Vulnerability

If you discover a security issue or vulnerability in this project, please:

1. **Do NOT open a public GitHub issue** with sensitive details.
2. Email the maintainers with a detailed report:  
   **rdwarkesh1300@gmail.com**  
3. Include:
   - Description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots / logs if available
   - Affected versions

We will respond within **5 business days**.

---

## 🔐 Supported Versions

| Version | Status        |
|---------|---------------|
| 1.0.0   | Supported     |
| <1.0.0  | Security fixes only |

Only officially released versions are supported for security updates.

---

## 🛡️ Security Guidelines

### 1. **API Keys & Secrets**
- Never commit API keys (e.g., `GEMINI_API_KEY`) into the repository.  
- Use environment variables (`.env`) or secret management tools.  
- Add all secrets to `.gitignore`.

### 2. **Dependency Management**
- Regularly update dependencies to mitigate known vulnerabilities (use tools like `dependabot`).  
- Before merging external changes, ensure:
  - Python dependencies (`requirements.txt`)
  - JavaScript libraries (via `package.json`)
  are up to date.

### 3. **Input Validation**
- All user inputs (especially any form data, file uploads, or API parameters) must be validated and sanitized.  
- Protect against injection attacks (SQL, command-line, prompt injection).  
- Validate video transcript data and repository metadata before processing.

### 4. **Authentication & Authorization**
- If you add user accounts or protected APIs, ensure proper auth checks.  
- Avoid exposing admin endpoints without strong safeguards.

### 5. **AI Prompt Safety**
- Since the app interacts with LLMs (Google Gemini), guard against **prompt injection attacks** by:
  - Filtering or limiting user-controlled text injected into prompts.  
  - Applying sanity checks and strict token limits before sending content to LLM APIs. :contentReference[oaicite:1]{index=1}

### 6. **Data Privacy**
- Do **not log sensitive user data** (API keys, personal info).
- If storing or processing demo transcripts, inform users and follow data minimization.

### 7. **Secure Frontend Practices**
- Use secure HTTP headers (CSP, X-Frame-Options).  
- Escape rendered UI content from untrusted sources.
- Avoid exposing secrets in the client bundle.

### 8. **Error Handling**
- Do not leak stack traces or environment info to clients.
- Log errors securely server-side without sensitive payloads.

---

## 📦 CI/CD & Build Security

- Set up automated scans using tools like:
  - **SAST / dependency scanners** (e.g., Bandit for Python, ESLint with security plugins).
  - **SBOM generation** for dependencies. :contentReference[oaicite:2]{index=2}
- Ensure builds fail if critical vulnerabilities are introduced.

---

## 🧪 Review & Testing

Before every major release:
- Conduct **static analysis**
- Perform **dependency vulnerability scans**
- Run **integration tests** covering AI integration components

---

## 🧠 Third-Party Services

This project uses external services (e.g., Google Gemini API):
- Only send necessary data — never send sensitive credentials.
- Review Terms & Privacy of each external API.

---

## 📝 Policy Updates

This Security Policy is a **living document** and will be updated as the project evolves or as new security threats emerge.

_Last updated: 📅 December 2025_

---
