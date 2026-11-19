# CLAUDE.md
Project rules live in AGENTS.md (shared with other agents). Follow them exactly.
@AGENTS.md

## Claude Code specifics
- One phase per session: after a Gate passes, tell the user to run `/clear` and paste the next prompt from docs/KICKOFF.md.
- You may run `bash tools/setup_env.sh` and `bash tools/get_data.sh` yourself (P0.2) if the human has not; skip get_data if `data/raw/finsurvival/Data` exists.
- Never read `.env`, keystores or anything under `data/` with Read; inspect data only through scripts that print summaries.
- `git push` only at the end of each phase.
