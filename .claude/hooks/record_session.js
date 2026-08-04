#!/usr/bin/env node
'use strict';

// Record every Claude Code dialog turn into sessions.md at the project root.
//
// Wired from .claude/settings.json as three hooks, all pointing here:
//   SessionStart     -> writes a dated session header
//   UserPromptSubmit -> appends your prompt (handed to the hook directly)
//   Stop             -> appends Claude's reply (read from the session transcript)
//
// Cross-platform by design: this runs under `node`, which ships inside Claude
// Code and is therefore guaranteed present on any machine that runs Claude —
// unlike `python`/`python3`, whose name differs (and breaks) across Windows and
// macOS. The script only appends to a file and never writes to stdout, so it
// injects nothing into Claude's context and can never block a turn.

const fs = require('fs');
const path = require('path');

function readStdin() {
  try {
    return fs.readFileSync(0, 'utf8');
  } catch (_) {
    return '';
  }
}

function projectDir(payload) {
  return process.env.CLAUDE_PROJECT_DIR || payload.cwd || process.cwd();
}

function stamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return (
    `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ` +
    `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
  );
}

// Join the visible text blocks of one message; ignore thinking / tool_use.
function extractText(content) {
  if (typeof content === 'string') return content.trim();
  if (Array.isArray(content)) {
    return content
      .filter((b) => b && b.type === 'text' && typeof b.text === 'string')
      .map((b) => b.text)
      .join('\n')
      .trim();
  }
  return '';
}

// A real user turn carries text; a tool result carries tool_result blocks.
function isRealUserPrompt(content) {
  if (typeof content === 'string') return content.trim().length > 0;
  if (Array.isArray(content)) {
    if (content.some((b) => b && b.type === 'tool_result')) return false;
    return content.some((b) => b && b.type === 'text');
  }
  return false;
}

// The full assistant reply for the turn that just ended: walk the transcript
// backwards, collecting every assistant text block until the turn's own user
// prompt (tool-result user messages are skipped, so multi-tool replies are
// captured whole).
function finalAssistantText(transcriptPath) {
  if (!transcriptPath) return '';
  let raw;
  try {
    raw = fs.readFileSync(transcriptPath, 'utf8');
  } catch (_) {
    return '';
  }
  const lines = raw.split('\n').filter((l) => l.trim());
  const chunks = [];
  for (let i = lines.length - 1; i >= 0; i--) {
    let obj;
    try {
      obj = JSON.parse(lines[i]);
    } catch (_) {
      continue;
    }
    const msg = obj.message || {};
    const role = msg.role || obj.type;
    if (role === 'user') {
      if (isRealUserPrompt(msg.content)) break; // reached this turn's prompt
      continue; // tool result — still part of this turn
    }
    if (role === 'assistant') {
      const t = extractText(msg.content);
      if (t) chunks.push(t);
    }
  }
  return chunks.reverse().join('\n\n').trim();
}

function main() {
  let payload = {};
  try {
    payload = JSON.parse(readStdin() || '{}');
  } catch (_) {
    process.exit(0);
  }
  const event = payload.hook_event_name || '';
  const logPath = path.join(projectDir(payload), 'sessions.md');
  const append = (s) => {
    try {
      fs.appendFileSync(logPath, s);
    } catch (_) {
      /* logging must never disrupt the session */
    }
  };

  if (event === 'SessionStart') {
    // Only for a genuinely new/resumed session — not on clear/compact/fork.
    if (payload.source === 'startup' || payload.source === 'resume') {
      const sid = String(payload.session_id || '').slice(0, 8);
      append(`\n\n---\n\n# Session ${sid} · ${stamp()}\n`);
    }
  } else if (event === 'UserPromptSubmit') {
    const prompt = String(payload.prompt || '').trim();
    if (prompt) append(`\n### 🧑 User · ${stamp()}\n\n${prompt}\n`);
  } else if (event === 'Stop') {
    const reply = finalAssistantText(payload.transcript_path);
    if (reply) append(`\n### 🤖 Claude · ${stamp()}\n\n${reply}\n`);
  }

  process.exit(0);
}

main();
