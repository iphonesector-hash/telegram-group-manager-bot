# Sector Koochooloo narrative engine

The narrative layer upgrades the existing pet, economy, equipment, games,
missions, social, boss and reminder systems. It does not replace them and does
not reset player progress.

## Player loop

1. The command hub reads the live narrative scene.
2. The scene explains why the next action matters.
3. The objective points to one existing system (care, game, shop, base, social,
   boss, chat or equipment).
4. The server verifies the action from authoritative database records.
5. The player claims the scene reward and unlocks the next scene.

The client never decides that an objective is complete. `sector_story.py`
builds the snapshot and validates every transition on the server.

## Current content

- World 1: Forgotten Land / 8 chapters / 40 scenes.
- World 2: Quantum Gate placeholder. World state is already persisted and can
  receive another eight-chapter content pack without a schema migration.
- Each chapter has a region, antagonist, five scenes, objectives, narrative
  copy, reward values and optional threat state.

## Compatibility

World number and scene activation time are stored in the existing
`SectorPet.inventory` JSON under namespaced `story:*` keys. Existing name, XP,
chapter, inventory, equipment and pet stats remain authoritative.

## Content expansion contract

New scenes are declared with `scene(title, text, objective, action, target,
coins, xp, threat)`. Every action must be mapped to an existing destination in
`ACTION_ROUTES` and validated by `objective_state`. Add a new validator before
publishing any scene that depends on a new gameplay system.

## Notification policy

Care reminders keep their existing cooldown. Narrative threat notifications
are sent once per scene and never more often than every six hours. Telegram
blocking disables reminders as before.
