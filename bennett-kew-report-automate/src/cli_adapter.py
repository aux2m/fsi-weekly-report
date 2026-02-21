"""
CLI Adapter: Wraps 'claude -p' subprocess calls for headless AI inference.
Uses the Max subscription (OAuth) instead of Anthropic API credits.
"""

import json
import asyncio
from pathlib import Path


async def call_claude(
    prompt: str,
    system_prompt: str = None,
    model: str = "sonnet",
    json_schema: dict = None,
    tools: str = None,
    allowed_tools: str = None,
    add_dir: str = None,
    timeout: int = 300,
) -> dict | str:
    """
    Call Claude CLI in non-interactive mode.

    Args:
        prompt: User message (piped via stdin to avoid Windows cmd length limit)
        system_prompt: Custom system prompt (replaces default)
        model: Model alias — opus, sonnet, haiku
        json_schema: JSON Schema dict for structured output
        tools: Space-separated tool names (e.g. "Read")
        allowed_tools: Tools to auto-approve (e.g. "Read")
        add_dir: Additional directory to allow tool access to
        timeout: Seconds before killing the process (default 300)
    Returns:
        Parsed JSON dict if json_schema provided, else raw text string.
    """
    cmd = [
        "claude",
        "-p",
        "--output-format", "json",
        "--model", model,
        "--no-session-persistence",
    ]

    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])
    if json_schema:
        cmd.extend(["--json-schema", json.dumps(json_schema)])
    if tools:
        cmd.extend(["--tools", tools])
    if allowed_tools:
        cmd.extend(["--allowed-tools", allowed_tools])
    if add_dir:
        cmd.extend(["--add-dir", add_dir])

    # Retry once on failure
    for attempt in range(2):
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=prompt.encode("utf-8")),
                timeout=timeout,
            )

            if proc.returncode != 0:
                err_msg = stderr.decode("utf-8", errors="replace").strip()
                if attempt == 0:
                    print(f"  CLI attempt {attempt+1} failed (exit {proc.returncode}): {err_msg[:300]}")
                    continue
                raise RuntimeError(f"claude CLI failed (exit {proc.returncode}): {err_msg[:500]}")

            output = stdout.decode("utf-8", errors="replace").strip()
            if not output:
                err_msg = stderr.decode("utf-8", errors="replace").strip()
                if attempt == 0:
                    print(f"  CLI attempt {attempt+1}: empty stdout. stderr: {err_msg[:300]}")
                    continue
                raise RuntimeError(f"claude CLI returned empty output. stderr: {err_msg[:500]}")

            envelope = json.loads(output)

            # --json-schema puts structured data in "structured_output", not "result"
            if json_schema:
                if "structured_output" in envelope and envelope["structured_output"]:
                    return envelope["structured_output"]
                # Fallback: try parsing result as JSON
                result_text = envelope.get("result", "")
                return json.loads(result_text)

            return envelope.get("result", "")

        except asyncio.TimeoutError:
            # Capture stderr for debugging before killing
            err_info = ""
            try:
                proc.kill()
                _, stderr_data = await asyncio.wait_for(proc.communicate(), timeout=5)
                err_info = stderr_data.decode("utf-8", errors="replace").strip()[:300]
            except Exception:
                pass

            if attempt == 0:
                msg = f"  CLI attempt {attempt+1} timed out after {timeout}s, retrying..."
                if err_info:
                    msg += f"\n  [stderr] {err_info}"
                print(msg)
                continue
            raise TimeoutError(
                f"claude CLI timed out after {timeout}s (2 attempts)"
                + (f"\n  stderr: {err_info}" if err_info else "")
            )

        except json.JSONDecodeError as e:
            raw = output[:300] if 'output' in dir() else ""
            if attempt == 0:
                print(f"  CLI attempt {attempt+1}: JSON parse error: {e}")
                if raw:
                    print(f"  [raw output] {raw}")
                continue
            raise RuntimeError(f"claude CLI returned invalid JSON: {e}\nRaw: {raw[:500]}")

    raise RuntimeError("claude CLI failed after 2 attempts")
