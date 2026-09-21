-- retry counter on tries
ALTER TABLE tries
  ADD COLUMN "attempt_slot";
