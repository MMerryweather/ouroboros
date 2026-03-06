# Codex Compatibility Contract

runtime_command_surface: AGENTS.md + skills/*/SKILL.md command routing in Codex session
invocation_context: Codex session for chat commands, bash shell for repository commands
identity_token_source: OPENAI_API_KEY for CodexAdapter, local OS user for filesystem
claude_plugin_manifest_role: legacy_only_non_runtime
legacy_claude_mcp_path_role: legacy_only_non_runtime
unsupported_features: none
gate_status: PASS
gate_reason: all critical contracts resolved
