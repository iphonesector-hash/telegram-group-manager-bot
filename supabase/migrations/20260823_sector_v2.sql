-- Sector Companion v2: allow all care/story action types.
-- Idempotent and safe for existing rows.
ALTER TABLE isectorbot_sector_pet_actions
  DROP CONSTRAINT IF EXISTS isectorbot_sector_pet_actions_action_check;

ALTER TABLE isectorbot_sector_pet_actions
  ADD CONSTRAINT isectorbot_sector_pet_actions_action_check
  CHECK (action IN ('charge','play','train','learn','repair','feed','clean','sleep','story'));
