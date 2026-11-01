# PLAY-89 — Allow removing a repository from a project, even when stories use it (DRAFT, not ready)

## Source
- PO message (imported issue): "currently where there is a story on a repo you can't remove it from project setting. Needed: to remove it from settings (stories can still hold the repo, but it's no longer used in new stories)."
- Epic PRD, User Story Backlog and Confluence research: not available to this intake. Parent epic, sibling stories and build order are unknown.

## Problem (as stated)
A project admin can't remove a repository from project settings while any story references it.

## Intended outcome (as stated)
- The admin can remove the repository from project settings even when stories reference it.
- Existing stories keep their reference to the repository.
- The removed repository is no longer used for new stories.

## Draft user story
As a project admin managing a project's repositories, I want to remove a repository from project settings even when existing stories reference it, so that new stories no longer use it while existing stories keep their reference. *(The persona and the "admin" role are not confirmed: Q6.)*

## Scope: unsettled
- In (stated): removing a referenced repo from project settings, keeping existing story references, and excluding the repo from new stories.
- Unknown: which product this lives in (Q1); whether removal is permanent or reversible (Q2); behaviour for stories in progress (Q3); how far the "not for new stories" exclusion reaches (Q4); confirmation or warning UX (Q5); who may remove (Q6).

## Acceptance criteria: not yet defined
These will be written once the questions are answered. Expected shape: a happy path (remove a referenced repo), a boundary (removed repo not offered for a new story), an edge case (story in progress on the removed repo), and an error or edge case (re-adding a removed repo).

## Open questions
- Q1 (P0): Target product: the Halo platform's project settings, or roeeoz/play1?
- Q2 (P0): Is removal permanent or reversible? Do re-added repos link back to old stories?
- Q3 (P0): Do stories still in progress keep working against the removed repo? Can they be retried or resumed? Do finished stories look different?
- Q4 (P0): Does the exclusion apply only to the repo choices at story creation, or also to import and epic breakdown when the repo is named explicitly?
- Q5 (P0): What confirmation or warning does the admin see when removing a repo that stories use?
- Q6 (P1): Who may remove a repo? Is the removal recorded where a user can see it?
- Q7 (P1): Parent epic and sibling dependencies.
- Q8 (P2): Should the project settings list show how many stories use each repo?
