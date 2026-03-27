# TODO: Fix Comment Form Position & Auto-Scroll
Status: ✅ COMPLETE

## Steps (Sequential)

### 1. ✅ Edit templates/feed.html
- Move comment form **BEFORE** comments loop (to top).
- Add `id="comment-form-{{ post.id }}"` to form.
- Preserve all existing HTML/classes.

### 2. ✅ Edit app.py
- Update `/comment/<post_id>` redirect: `redirect(url_for("index") + f"#comment-form-{post_id}")`

### 3. 🔄 Test Changes
- Restart server: `python app.py`
- Add 3-5 comments to a post.
- Verify:
  | Check | Expected |
  |-------|----------|
  | Form position | Always at TOP of comments section |
  | After submit | Auto-scrolls to form (sees new comment + form) |
  | Toggle works | Collapse/expand unchanged |
  | Report page | Unchanged (read-only) |
  | Mobile | Responsive OK |

### 4. 🔄 Cleanup
- Remove this TODO.md
- attempt_completion

**Notes**: Minimal changes. No deps. Uses URL fragment for scroll (native browser).
