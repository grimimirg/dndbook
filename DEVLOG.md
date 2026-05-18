# D&D Book — Dev Log

A living document of what we built, what broke, what we learned, and why things are the way they are. Written for us, not for the internet.

---

## The Stack and Why

**Backend:** Flask + SQLAlchemy + Flask-Migrate + Flask-SocketIO, running in Docker, PostgreSQL as the database.

Flask was chosen for its simplicity and transparency — you see exactly what's happening. The architecture follows a strict three-layer pattern: controllers handle HTTP, services handle business logic, models handle data. This keeps things testable and readable. Don't collapse these layers even when it's tempting.

**Frontend:** Vue 3 (Composition API) + Pinia + Vite + vue-i18n. No component-level `<style>` blocks — all CSS lives in `fe/src/style.css`. This was a deliberate choice: one file means one place to look, and it forces you to think in terms of shared design rather than isolated component styles.

**Database driver:** `psycopg[binary]>=3.1` — this is psycopg **3**, not psycopg2. The SQLAlchemy URL must use `postgresql+psycopg://` (not `postgresql+psycopg2://`). We got burned by this: a wrong prefix causes silent connection failures with no clear error message. The two drivers are not drop-in replacements for each other.

---

## Deployment: The Render Story

We deployed to Render.com free tier: a Docker Web Service for the backend, a Static Site for the frontend build, and a managed PostgreSQL database.

### What went wrong and how we fixed it

**Problem 1: DATABASE_URL missing.**
Render doesn't automatically wire the database URL to the web service. You have to set it manually in the Environment section, using the *internal* connection string (faster, no SSL needed within Render's network) for the app, and the *external* connection string (with `?sslmode=require`) for any local access.

**Problem 2: Wrong driver prefix.**
The DATABASE_URL we set used `postgresql+psycopg2://` because that's what you find in most tutorials. Our `requirements.txt` only has psycopg3. The app started, appeared to connect, then failed. Changing the prefix to `postgresql+psycopg://` fixed it.

**Problem 3: Multiple Alembic migration heads.**
Two migrations had been created independently from the same parent revision, creating two "heads" in the migration graph. `flask db upgrade head` (singular) fails in this case. The fix is either `flask db upgrade heads` (plural) or creating a merge migration with `flask db merge heads`. We added a merge migration file (`a65525709835_merge_heads.py`) and updated the code to use `revision='heads'`.

**Problem 4: Migration revision IDs too long.**
`alembic_version.version_num` is `varchar(32)`. We had revision IDs like `add_related_invite_id_to_notifications` (38 characters). PostgreSQL silently truncated them on insert, which corrupted the Alembic state tracking and caused the app to fall back to `db.create_all()`. This is the silent kind of failure — everything *seems* to work, but future migrations will be confused because Alembic thinks no migration has ever been applied.

The fix: rename all non-standard revision IDs to 12-character hex strings (the Alembic default format), update all `down_revision` references, and manually stamp the production database with the correct head revision using psycopg3 directly:

```python
import psycopg
conn = psycopg.connect("postgresql://...?sslmode=require")
cur = conn.cursor()
cur.execute("DELETE FROM alembic_version")
cur.execute("INSERT INTO alembic_version (version_num) VALUES ('a65525709835')")
conn.commit()
```

**Problem 5: Bash heredoc vs inline Python.**
`init-and-start.sh` originally ran an inline Python snippet inside bash double quotes. This caused bash string escaping issues with Python f-strings (the `{e}` in `f'error: {e}'` was interpreted by bash). We switched to a heredoc (`python3 << 'PYCHECK'` ... `PYCHECK`) which passes the script verbatim to Python.

**The db.create_all() fallback:**
The startup script falls back to `db.create_all()` if migrations fail. This creates tables but doesn't stamp Alembic — so after a fallback, the app works but the migration system is in an unknown state. Every time we deploy and migrations fail silently, we accumulate technical debt. Always fix the root cause. The fallback exists for emergency situations, not as a normal path.

---

## i18n: Five Languages, One Source of Truth

The app supports Italian, English, French, German, and Spanish. All strings live in YAML files under `fe/src/locales/`. Italian (`it.yaml`) is the primary language — write Italian first, then translate.

**The rule:** every key must exist in all five files. Missing a key produces either a silent fallback (showing the key name) or a visible `[key]` placeholder. There's no automatic warning at build time, so you have to be disciplined about it.

**Practical tip:** when adding a new feature, add all its keys to all five files in the same commit. Don't defer translations — they're easy to forget and tedious to reconstruct later.

We also use `locale` from `useI18n()` reactively in components. This means locale-aware logic (like the campaign generator) responds to runtime language changes without a page reload.

---

## CSS: One File to Rule Them All

`fe/src/style.css` is the single stylesheet. No scoped styles, no CSS modules. This sounds like it would become a mess — in practice it's fine because the codebase is coherent and the components are well-named.

The discipline required: always search for existing rules before adding new ones. If you add `.panel-header` styles in two places, you'll get conflicts you can't easily trace.

**The width lesson:** we had the `campaign-description-panel` hardcoded to `width: 380px` while its siblings (characters panel, players panel) had no width set. Result: the description panel appeared slightly wider because it forced the column to 380px, but the siblings only stretched to fit their content — which was slightly less. The fix: put `width: 380px` on the *column container* and `width: 100%` on all children. Width belongs on the container, not on individual panels.

**CSS variables for theming:** the app supports dark and light themes via `data-theme` attribute on `:root`. All colors reference CSS variables (`--text-primary`, `--card-bg-1`, `--border-color`, etc.). When adding new UI elements, always use variables — never hardcode `#2a2a2a` or similar. Check both themes when reviewing UI work.

---

## The Campaign Generator

We built a zero-cost, zero-API weighted random campaign setup generator in pure JavaScript (`fe/src/utils/campaignGenerator.js`), inspired by the Perchance generator syntax.

**Why not use the LLM API?** It would work perfectly and cost almost nothing per call — but for something that runs on a free-tier server and could be called repeatedly, weighted random is the right tool. It's instant, offline-capable, and produces output that's just as charming as AI-generated text for this use case.

**The Perchance model:** items in an array can be plain strings or `[value, weight]` pairs. A weight of `0.5` means half as likely to be picked as an unweighted item. We implemented this as a `pick()` function that calculates a weighted total and walks the array.

**The bug we hit:** we originally stored antagonist/objective pairs as `[narrativeText, label]` arrays. The `pick()` function saw these as `[value, weight]` — so `label` (a string) became the weight, causing JavaScript type coercion chaos. Fix: use objects `{n: narrativeText, l: label}` for paired data. `pick()` only treats two-element arrays as `[value, weight]`.

**Italian grammar:** prepositions in Italian contract with articles. `"Nelle" + "i boschi"` = `"Nelle i boschi"` (wrong). We fixed this by embedding the full contraction in each location prefix: `"Nei boschi maledetti di"` instead of `"i boschi maledetti di"`.

**Locale-aware:** generates Italian for the `it` locale, English for everything else. The vocabulary objects are `it` and `en` in the same file — add to both when extending.

---

## UX Decisions and Why

**Hamburger menu logout button:** originally labeled "ESCI" at the bottom of the hamburger menu, easily confused with "close the menu." We replaced it with a visually distinct red-tinted button inside an "Account" section separated by a decorative line, making it clear it's a destructive action.

**Drag & drop for images:** added to both the character creation modal and the post creator. The drop zone in the post creator sits next to the "Add images" button using `align-items: stretch` on the container so both elements share the same height. The character modal's drop zone wraps the entire upload area with a dashed border that highlights on drag-over.

**Auto-enter campaign on creation:** when you create a campaign, you should land inside it immediately. The bug was that `handleCreateCampaign` called `setCurrentCampaign()` but didn't set `expandedCampaignId` or call `fetchPosts()`. Both are required — the first expands the campaign in the tree UI, the second loads the post feed. Without either, the UI looks unchanged even though the store state is updated.

**Hidden posts and notifications:** a post marked "hide from players" should not notify players of its existence. We added `is_hidden` as a parameter to `PostsService.create_post()` and skip `create_notification_entries()` when it's `True`. This required passing `is_hidden` through from the frontend store all the way to the service layer.

**Predefined character toggle:** defaulted to unchecked, which meant every DM had to manually check it. Changed to checked by default since most characters created by a DM in the context of a campaign are intended to be predefined/pickable by players.

---

## Things We'd Do Differently

**Migration IDs from day one.** Use `flask db revision` to generate migrations — never write the revision ID by hand as a descriptive string. The varchar(32) limit is a silent trap.

**Single driver, documented upfront.** The psycopg3 vs psycopg2 distinction should be the first line of the setup docs. It's the kind of mistake you make once and remember forever.

**Width on containers, not children.** Learned this from the left column alignment bug. It's a general CSS principle but easy to forget when you're adding styles to a specific component.

**Test the generator with many runs before shipping.** The pick() bug wasn't obvious from reading the code — it only showed up in the output as truncated labels. A quick loop of 100 generated outputs would have caught it immediately.

---

## Open Threads

- The `db.create_all()` fallback in `init-and-start.sh` should eventually be removed once we're confident migrations always run cleanly. It's a safety net that masks problems.
- The campaign generator vocabulary is small. More location names, more antagonist types, more hooks would make the output feel less repetitive over time.
- Branch `claude/fix-issue-SWt2t` contains all the work from this session and needs to be merged to `main`.
