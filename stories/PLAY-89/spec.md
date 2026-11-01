# PLAY-89: Allow removing a repository from a project, even when stories use it (DRAFT, not ready)

## Source
- PO message (imported issue): "currently where there is a story on a repo you can't remove it from project setting. Needed: to remove it from settings (stories can still hold the repo, but it's no longer used in new stories)."
- PO message (intake follow-up): "no epic, nothing blocked. Removal is via project settings which is already gated to admins."
- Parent epic: none (PO message). This is a standalone story with no sibling dependencies.

## Problem (as stated)
A project admin can't remove a repository from project settings while any story references it.

## Intended outcome (as stated)
- The admin can remove the repository from project settings even when stories reference it.
- Existing stories keep their reference to the repository.
- The removed repository is no longer used for new stories.

## User story
| Field | Value |
| --- | --- |
| Persona / Role | Project admin managing the project's repositories in project settings (confirmed, PO message) |
| User story | As a project admin, I want to remove a repository from project settings even when existing stories reference it, so that new stories no longer use it while existing stories keep their reference. |
| Context | Removal happens in project settings, which only admins can already reach (PO message). Today a repo that any story references can't be removed. In: removing a referenced repo, keeping existing stories' references to it, and excluding it from new stories. Out: changing who can reach project settings. Still open: which product this lives in (Q1), how far the exclusion reaches (Q4), whether removal is reversible (Q2), and what the admin sees (Q5). |
| Traces to | PO message (imported issue) |
| Priority | not set: the PO has not stated one |
| Size | not estimated until Q1 is answered |
| Pre-conditions | Project settings already restrict repo management to admins (PO message) |
| Blockers | Q1, Q2, Q3, Q4, Q5 below. No working assumptions are taken: the intake bar forbids guessing. |
| Depends on | — |

## Acceptance criteria: not yet defined
These will be written once Q1 to Q5 are answered. Expected coverage:
- Happy path: remove a repo that stories reference.
- Boundary: the removed repo is not offered for a new story.
- Edge case: a story still running on the removed repo.
- Edge or error case: re-adding a removed repo, or a story that names the removed repo explicitly.

## Open questions
- Q1 (P0): Target product: the Halo platform's project settings, or roeeoz/play1? play1 has no projects, repositories or settings today.
- Q2 (P0): Is removal permanent, or does the repo stay listed as removed or inactive? Can an admin re-add it, and if so do the old stories link to it again?
- Q3 (P0): The PO said "nothing blocked." Confirm what that covers: do stories still running on the removed repo keep cloning, pushing, opening PRs, retrying and resuming as normal? Should finished stories look any different?
- Q4 (P0): Does "no longer used in new stories" only remove the repo from the choices when a story is created? Or does "nothing blocked" mean that importing a story or breaking down an epic that names the repo explicitly is still allowed?
- Q5 (P0): What confirmation or warning does the admin see when removing a repo that stories use?
- Q6 (resolved): Only admins can remove, through the existing admin-gated project settings (PO message). Still open (P2): is the removal recorded anywhere a user can see?
- Q7 (resolved): No parent epic and no sibling dependencies (PO message).
- Q8 (P2): Should the project settings list show how many stories use each repo?
