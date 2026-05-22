# Ultimate Edition Roadmap

## Architecture & Platform
- [x] Plugin-based game interface and registry
- [x] Scene/state manager and fixed timestep loop
- [x] Shared input/audio/settings/profile/ui services
- [ ] Hot-reload plugin discovery
- [ ] Per-game config manifests
- [ ] Event bus for cross-system messaging
- [ ] Dependency injection container
- [ ] In-game console commands
- [ ] Replay capture + playback
- [ ] Save migration/versioning

## Physics & Feel
- [x] Physics abstraction with fallback backend
- [x] Optional `pymunk` backend integration
- [x] Collision layers/masks helpers
- [x] Moving platform helper
- [x] Hit-stop + screen shake utilities
- [ ] One-way platform support
- [ ] Slope snapping support
- [ ] Sensor/trigger volume helpers
- [ ] Deterministic re-simulation checks
- [ ] Rigidbody debug visualization

## Rendering / 2.5D / VFX
- [x] Parallax layer renderer
- [x] Mode-7 style projection helper
- [x] 2.5D demo scene/plugin
- [ ] Sprite batching pipeline
- [ ] Palette/theme shader emulation
- [ ] Lighting pass helper
- [ ] Dynamic shadows (blob)
- [ ] Camera rails and cinematic pans
- [ ] Weather overlays
- [ ] CRT/post-process toggle

## Gameplay Framework
- [x] Main menu game selector
- [x] Breakout plugin mini-game
- [x] Twin-stick plugin mini-game
- [x] Physics mini pinball plugin
- [x] Legacy cabinet compatibility launcher
- [ ] Power-up registry shared module
- [ ] Enemy behavior trees
- [ ] Procedural challenge generators
- [ ] Boss phase framework
- [ ] Local multiplayer input router

## UX, Accessibility, and Meta
- [ ] Accessibility presets (color/contrast)
- [ ] Reduced motion profile
- [ ] Remappable controls UI
- [ ] Audio mixer categories
- [ ] Subtitle-like event captions
- [ ] Per-game tutorials
- [ ] Achievements + unlocks
- [ ] Daily/weekly challenge queue
- [ ] Progression economy and cosmetics
- [ ] Cloud save adapter interface

## Tooling & Quality
- [x] Ruff/Black-style formatting config
- [x] Minimal GitHub Actions lint/test workflow
- [x] Unit tests for shared helpers
- [ ] Coverage reporting
- [ ] Type-checking in CI
- [ ] Benchmarks for update loops
- [ ] Asset linting checks
- [ ] Packaged release automation
- [ ] Signed build artifacts
- [ ] Contributor templates and labels
