# PLAY-89: Allow removing a repository from a project, even when stories use it (DRAFT, not ready)

## Source
- PO message (imported issue): "currently where there is a story on a repo you can't remove it from project setting. Needed: to remove it from settings (stories can still hold the repo, but it's no longer used in new stories)."
- PO message (intake follow-up): "no epic, nothing blocked. Removal is via project settings which is already gated to admins."
- PO message (verification turn): "the target product is the playground guestbook API settings; no further details yet."
- Parent epic: none (PO message). This is a standalone story with no sibling dependencies.

## What the target product has today
The playground guestbook API (roeeoz/play1, branch halo/feat/play-89) has only two capabilities: posting a guestbook entry and listing guestbook entries. It has no settings, projects, repositories, stories, admin role or access control. As a result:
- the problem as stated ("you can't remove a referenced repo") can't be reproduced in this product;
- the earlier statement that settings are "already gated to admins" doesn't hold here (see Q1 and Q2).

## Problem (as stated)
A project admin can't remove a repository from project settings while any story references it.

## Intended outcome (as stated)
- The admin can remove the repository from project settings even when stories reference it.
- Existing stories keep their reference to the repository.
- The removed repository is no longer used for new stories.

## User story
| Field | Value |
| --- | --- |
| Persona / Role | Project admin managing the project's repositories in the guestbook API's settings. Not yet confirmed: the guestbook API has no admin role (Q2). |
| User story | As a project admin, I want to remove a repository from project settings even when existing stories reference it, so that new stories no longer use it while existing stories keep their reference. |
| Context | Target product: the playground guestbook API's settings (PO message). That product has no settings, projects, repositories or stories today, so the story either adds them first (scope far beyond "allow removal") or means something not yet identified (Q1). In: removing a referenced repository, keeping existing stories' references to it, and excluding it from new stories. Out: not yet defined. Still open: Q1 to Q5. |
| Traces to | PO message (imported issue), PO messages at intake |
| Priority | not set: the PO has not stated one |
| Size | not estimated until Q1 is answered (it may be XL and need splitting) |
| Pre-conditions | Not yet known. The admin gating stated by the PO doesn't exist in the guestbook API (Q2). |
| Blockers | Q1 to Q5 below. No working assumptions are taken: the intake bar forbids guessing. |
| Depends on | — |

## Acceptance criteria: not yet defined
These will be written once Q1 to Q5 are answered. Expected coverage:
- Happy path: an admin removes a repository that stories reference.
- Boundary: the removed repository is not used for a new story.
- Edge case: an existing story that references the removed repository still shows and keeps that reference.
- Error case: a non-admin tries to remove a repository; a new story names the removed repository explicitly.

## Open questions
- Q1 (P0): Answered in part: the target is the playground guestbook API's settings. Still open: that API has no settings, projects, repositories or stories. Is the story meant to create them? If so, it should be split. Or is there an existing capability that was meant?
- Q2 (P0): Who is an admin in the guestbook API, which has no roles or access control? Is refusing a non-admin's removal part of this story?
- Q3 (P0): Is removal permanent, or does the repository stay listed as removed or inactive? Can an admin re-add it, and if so do the old stories link to it again?
- Q4 (P0): "Nothing blocked" and "no longer used in new stories": what happens when a new story names a removed repository (refused, warned, or allowed)? Do existing stories keep working and showing the repository unchanged?
- Q5 (P0): What confirmation or warning does the admin see when removing a repository that stories use?
- Q6 (P2): Is the removal recorded anywhere a user can see?
- Q7 (resolved): No parent epic and no sibling dependencies (PO message).
- Q8 (P2): Should the settings list show how many stories use each repository?
