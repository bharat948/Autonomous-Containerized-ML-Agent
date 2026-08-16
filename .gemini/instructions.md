# Project Road Map and Guidelines: Atomic Sandbox Agent

This project aims to build an encapsulated ML/General Agent running inside a Docker sandbox. To maintain reliability and developer sanity, the development process follows strict **atomic, test-driven phases**. 

## Development Philosophy
1. **Never write untested code**: Each feature must have a corresponding verification step or test script.
2. **Build incrementally (Baby Steps)**:
   - **Phase 1**: Environment setup (Docker sandbox container only).
   - **Phase 2**: Directory mounts & shared volumes (Verify write file from host -> read in container and vice-versa).
   - **Phase 3**: Basic agent scaffold (Can construct a prompt and call the LLM API).
   - **Phase 4**: Add a single execution tool (Agent can run code inside container via `docker exec`).
   - **Phase 5**: More specialized tools & evaluations (e.g. Kaggle datasets).

---

## Command Reference

### Docker Container Management
- **Startup Script**: `./setup_sandbox.sh`
- **Teardown Script**: `./teardown.sh`
- **Verification Script**: `./verify_sandbox.sh`

### File Mount Structure
- Host: `/home/bharat/explore/workspace` (or the project root)
- Sandbox: `/workspace`
