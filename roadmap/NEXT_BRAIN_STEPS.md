# Next Brain Steps

## Phase 1: Write Mode Contract

- Load `configs/kodex_write_policy.json`
- Validate generated file paths
- Enforce max file count and byte limits
- Create checkpoint before apply
- Stop before commit

## Phase 2: Provider Activation

- Keep `noop` as default
- Add OpenAI provider behind explicit env/config
- Add Ollama provider behind local endpoint config
- Normalize provider outputs to one file-plan schema

## Phase 3: Repair Loop

- Run checks
- Diagnose failure logs
- Request repair candidate from provider
- Validate repair write plan
- Apply only if safe
- Stop after max attempts

## Phase 4: App Builder

- Compile README/SPEC/AGENTS into structured product model
- Build repo context
- Generate multi-file implementation
- Validate and preview
- Apply with approval
