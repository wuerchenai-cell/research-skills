---
name: research-career
description: Use when the user asks about funding applications (grants, scholarships, CSC), patent filing and tracking, job/postdoc applications, teaching assistant duties, lab onboarding, cross-group collaboration, idea capture, or meeting notes. Also use for research CV preparation, career planning, or academic job market preparation. Does not handle literature deep reading, experiment design, or manuscript writing—use research-read / research-study / research-find for those.
---

# Research Career

## Purpose

Track and manage the career-development side of research life: funding, patents, jobs, teaching, collaboration, ideas, and meetings. Produce durable artifacts that help you stay organized across multiple deadlines and applications.

## Non-negotiable rules

1. Never invent grant numbers, patent IDs, acceptance rates, salary ranges, or committee decisions.
2. Always check current official call details, eligibility, deadlines, and scoring criteria before drafting.
3. Separate confirmed facts (you submitted, you passed) from tentative observations (you might be eligible).
4. Keep the user responsible for final submission, funding, patent, and career decisions.
5. Preserve negative outcomes and rejections; they are evidence for future applications.

## Task router

| User goal | Primary mode | Load |
|---|---|---|
| Apply for grants, scholarships, CSC, or funding | `grant-tracker` | `modules/grant-tracker/module.md` |
| Track patent filing, prosecution, or grant | `patent-tracker` | `modules/patent-tracker/module.md` |
| Prepare CV, job applications, postdoc search | `career` | `modules/career/module.md` |
| Record teaching duties, assignments, or Q&A | `teaching` | `modules/teaching/module.md` |
| Onboard to a new lab or group | `lab-onboarding` | `modules/lab-onboarding/module.md` |
| Register cross-group collaboration | `collaboration` | `modules/collaboration/module.md` |
| Capture fleeting ideas or research diary | `idea-capture` | `modules/idea-capture/module.md` |
| Record meeting or seminar decisions | `meeting-notes` | `modules/meeting-notes/module.md` |

## Workflow

### 1. Identify the task type

Route the request to the matching module. If the request spans multiple modules (e.g., a grant application that also needs CV updates), handle each module separately.

### 2. Load the module

Read `modules/<module-id>/module.md` before acting. Use the module's templates to create or update tracking files.

### 3. Keep records honest

- Mark status transitions explicitly (submitted → accepted/rejected → resubmit).
- Record the date of each status change.
- Preserve rejection reasons and feedback for future applications.
- Do not inflate achievements or hide failures.

### 4. Produce a summary

After each career task, provide a brief summary:
- what was updated;
- what evidence supports it;
- what needs user confirmation or follow-up.

## Module overview

| Module | Tracks | Template |
|---|---|---|
| `grant-tracker` | Grants, scholarships, CSC applications | `templates/grant-tracker.csv` |
| `patent-tracker` | Patent filing, prosecution, grant | `templates/patent-tracker.csv` |
| `career` | Job applications, postdoc search, CV | `templates/career.csv` |
| `teaching` | TA duties, assignments, Q&A | `templates/teaching.md` |
| `lab-onboarding` | Lab environment, accounts, norms | `templates/lab-onboarding.md` |
| `collaboration` | Cross-group roles, IP, sharing | `templates/collaboration.md` |
| `idea-capture` | Fleeting ideas, research diary | `templates/idea-capture.md` |
| `meeting-notes` | Meeting decisions, action items | `templates/meeting-notes.md` |

## Dependencies

This skill is self-contained: module templates, instructions, and the bundled
scripts live in this package. Scripts read and write only under the
`skill辅助（用户无需打开，辅助skill使用）/` support directory of the project
you point them at (`--project`); they never move or modify user materials.

## Portability

Module templates and instructions are shareable. User data lives inside the project and never enters a runtime package.

## Maintenance

Only an explicit user maintenance request may change this skill. This skill has no external maintenance protocol; use the maintenance rules already recorded in this SKILL.md.
