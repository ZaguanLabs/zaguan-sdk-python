# Zaguan SDK Testing & Versioning Guide

This document describes how to **test** a Zaguan SDK and how to manage its **versioning** and compatibility with Zaguan CoreX.

## 1. Testing Strategy

### 1.1 Golden-Path Tests

These are the basic tests that must always pass.

**Non-streaming chat**

- [ ] Simple prompt → response:
  - Call `chat` with a trivial prompt and a well-known model.
  - Assert non-empty `choices[0].message.content`.
- [ ] Tools:
  - Define a simple tool.
  - Send a prompt that triggers a tool call.
  - Verify tool call structure is present in the response.
- [ ] Provider-specific parameters:
  - Pass a provider-specific option (e.g. Gemini reasoning flags) via `providerOptions`.
  - Verify the request body contains these options (via logging or test doubles, if necessary).

**Streaming chat**

- [ ] Start a streaming request and:
  - Consume all chunks.
  - Assert that at least one non-empty `delta` is received.
  - Assert a `finish_reason` is eventually seen.
- [ ] Cancellation:
  - Start a streaming request.
  - Cancel it partway through.
  - Assert stream terminates without leaking resources.

### 1.2 Cross-Provider Scenarios

Test with multiple providers configured in CoreX (actual available models depend on your deployment). Examples:

- `openai/gpt-4o-mini`
- `google/gemini-2.0-flash`
- `anthropic/claude-3-opus` (via OpenAI-compatible routing if used)
- `deepseek/deepseek-reasoner`
- `perplexity/sonar-reasoning`

For each:

- [ ] Call `chat` and ensure:
  - Response is successfully parsed.
  - `usage` fields are populated where expected.
- [ ] Optionally, compare behavior across providers for the same prompt to ensure the SDK doesn’t embed provider-specific assumptions.

### 1.3 Reasoning Tokens

For providers that support reasoning tokens and where CoreX exposes them:

- [ ] Send a prompt that exercises reasoning (complex task).
- [ ] Assert `usage.completionTokensDetails.reasoningTokens` is greater than zero (when provider supports it).

For providers that don’t expose reasoning tokens (e.g. Perplexity’s `<think>` approach):

- [ ] Assert `reasoningTokens` is absent or zero.
- [ ] Ensure SDK behavior is documented and does not treat this as an error.

### 1.4 Error Cases

Test at least the following scenarios:

- [ ] Invalid API key
  - Expect 401/403 and a structured error.
- [ ] Unknown model ID
  - Expect 4xx with a meaningful message.
- [ ] Credits exhausted (if credits enabled)
  - Expect an appropriate error and/or lack of response depending on server behavior.
- [ ] Network errors (e.g., dial failure, timeout)
  - Ensure the SDK surfaces these as recognizable errors.

### 1.5 Credits Endpoints (If Used)

- [ ] `getCreditsBalance` returns a valid structure for a known test user.
- [ ] `getCreditsHistory` returns a list and respects pagination/limits.
- [ ] `getCreditsStats` returns stats with reasonable fields populated.

## 2. Compatibility Expectations

### 2.1 Alignment with CoreX Behavior

SDK behavior must stay aligned with Zaguan CoreX:

- When CoreX adds fields to responses, SDKs should continue working without changes (ignore unknown fields).
- When CoreX adds new optional request fields, SDKs should be able to forward them via generic `providerOptions` / `extra` fields, until they are modeled explicitly.

### 2.2 Public API Stability

- **Breaking changes** to the SDK’s public API require a **major version bump**.
- Minor and patch versions should remain backward compatible at the API level.

Examples of breaking changes:

- Renaming or removing public methods.
- Changing parameter types in a backward-incompatible way.
- Changing return types in a backward-incompatible way.

Non-breaking changes:

- Adding new optional parameters with sensible defaults.
- Adding new fields to response types that are optional.
- Adding new helper methods or utilities.

### 2.3 Mapping to CoreX Versions

It is recommended to **document** which range of CoreX versions an SDK version has been tested against, for example:

- `zaguansdk-go v1.2.0` tested with `Zaguan CoreX v0.20.x`.

This does not need to be strict semantic coupling, but it gives users guidance.

## 3. Versioning Guidelines

### 3.1 Semantic Versioning

SDKs should use **semantic versioning**:

- `MAJOR.MINOR.PATCH`

Rules:

- Increment **PATCH** for:
  - Bug fixes.
  - Non-breaking internal changes.
- Increment **MINOR** for:
  - New backward-compatible features.
  - New endpoints or optional parameters.
- Increment **MAJOR** for:
  - Breaking changes to the public API.

### 3.2 Deprecation Policy

When an API is going to change:

- Prefer **deprecating** old methods first rather than removing them immediately.
- Warn in documentation and release notes.
- Only remove deprecated APIs in the next major version.

## 4. CI/CD & Automation (Recommended)

For official SDKs, it is recommended to:

- Run tests against:
  - Local CoreX instance.
  - Optionally, a staging environment.
- Include tests for:
  - Multiple providers.
  - Streaming.
  - Credits endpoints (when available).
- Automate publishing of SDK packages upon tagging releases.

## 5. Optional: Zaguan-Native Higher-Level API

If a higher-level, Zaguan-native API is added on top of the OpenAI-compatible layer, it should have its own small test suite, including:

- `chatVirtual` style operations.
- Routing hints and fallback logic.
- Reasoning controls that abstract over provider differences.

This layer should be versioned in sync with the core SDK, and any breaking changes to it must follow the same semantic versioning rules.

---

A Zaguan SDK that follows the design docs in `docs/SDK` and passes the tests described here can be considered **production-ready** and suitable as an official or reference implementation.
