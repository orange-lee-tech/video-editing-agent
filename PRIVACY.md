# Privacy Policy

**Last updated:** 2026-09-18

This Privacy Policy applies to the **video-editing-agent / 有岐** project maintained by **orange-lee-tech** and available at:

- https://github.com/orange-lee-tech/video-editing-agent
- https://github.com/orange-lee-tech

## 1. Local-first processing

video-editing-agent is designed as a local-first desktop video-editing application. User-selected media, project files, intermediate artifacts, and rendered outputs are intended to be processed and stored on the user's own device unless the user chooses a feature or provider configuration that requires data to be sent to an external service.

The project does not intentionally upload a user's local media to a developer-operated server merely by virtue of opening or editing that media.

## 2. Information the application may process

Depending on the features used, the application may process information such as:

- video, audio, images, subtitles, and other media selected by the user;
- prompts, editing instructions, project metadata, timestamps, and generated editing plans;
- application logs, diagnostic information, and locally generated intermediate files;
- credentials or API keys that the user provides for optional third-party services.

Such information is used to provide the requested editing, analysis, rendering, troubleshooting, or related application functionality.

## 3. Third-party AI and service providers

Some features may rely on third-party AI models, APIs, or other services configured or selected by the user. When such a feature is used, the data required for that request may be transmitted directly to the relevant provider.

The handling of information by a third-party provider is governed by that provider's own privacy policy, terms, retention rules, and security practices. Users should review those policies before enabling or using an external provider.

Providers currently supported or referenced by the application include:

- **DeepSeek API** — API documentation and applicable Open Platform terms are published at <https://api-docs.deepseek.com/>; DeepSeek's privacy policy is published by DeepSeek at <https://platform.deepseek.com/downloads/DeepSeek%20Privacy%20Policy.pdf>.
- **Google Gemini API** — Gemini API documentation and data-handling guidance are published at <https://ai.google.dev/gemini-api/docs/>; Google's privacy policy is at <https://policies.google.com/privacy>.
- **OpenAI API** — API/service data is governed by the applicable OpenAI customer/service agreements and data controls; OpenAI privacy and data-use information is published at <https://openai.com/policies/privacy-policy/> and <https://help.openai.com/en/articles/10306912>.

Provider terms and privacy practices can change independently of this project. The user is responsible for reviewing the current provider terms that apply to the account and service tier they choose.

## 4. API keys and credentials

Users are responsible for protecting credentials they configure for third-party services. Credentials should not be committed to the public GitHub repository or otherwise shared publicly.

The project is designed to avoid treating user credentials as project content. Any storage or transmission of credentials required by a configured provider should be limited to what is necessary to enable that provider.

The application does not bundle developer-owned production API credentials for these optional providers.

## 5. Public update channel and GitHub infrastructure

When the user invokes the software update check, the application retrieves public update metadata from project-controlled public web infrastructure and may subsequently open or download an official GitHub Release artifact.

The update check sends a normal HTTPS request containing standard network information and a product/version User-Agent. It does **not** upload the user's source media, project database, editing instructions, API keys, or rendered output as part of the update check.

GitHub and GitHub Pages may process ordinary connection metadata such as IP address, request information, and browser/network metadata under GitHub's own privacy terms. GitHub's privacy statement is published at <https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement>.

## 6. Data collection by the project maintainer

The project is currently distributed through GitHub and is designed primarily for local execution. The project maintainer does not intentionally operate a centralized service for collecting users' source media, project files, or rendered videos as part of normal local use.

GitHub itself may collect information when users visit or interact with GitHub-hosted project pages. That activity is governed by GitHub's own privacy policies.

## 7. Data retention and deletion

Local project data remains under the user's control and may be deleted using the user's operating system or the application's available project-management functions.

For data transmitted to an external provider, retention and deletion are subject to that provider's policies and the user's account settings with that provider.

## 8. Sharing of information

The project maintainer does not sell users' personal information.

Information may be shared with external providers only when required by functionality the user chooses to invoke, or when disclosure is required by applicable law.

## 9. Security

Reasonable efforts are made to keep local/private media, credentials, toolchains, and generated private artifacts out of the public source repository. However, no software or transmission method can guarantee absolute security. Users should avoid submitting secrets or sensitive personal information to public GitHub issues, discussions, or pull requests.

## 10. Children's privacy

The project is not specifically directed to children and is not intended to knowingly collect children's personal information through a developer-operated service.

## 11. Changes to this policy

This Privacy Policy may be updated as the project, supported providers, or data flows evolve. Material changes will be reflected in this file and its Git history.

## 12. Contact

For privacy-related questions about this project, contact the maintainer through the **orange-lee-tech** GitHub account:

https://github.com/orange-lee-tech

Please do not include passwords, API keys, private media, or other sensitive personal information in a public GitHub issue.
