# Papers

**My papers** keeps the papers a student reads, apart from their courses, so each paper can be studied as a whole:
read by its sections, noted, summarised and asked about, on its own or with the other papers of its collection. The
behaviour is specified in [`features/papers.feature`](../features/papers.feature) and
[`features/ui_papers.feature`](../features/ui_papers.feature).

- [Collections](#collections)
- [Adding a paper](#adding-a-paper)
- [A paper's details](#a-papers-details)
- [Reading and notes](#reading-and-notes)
- [Asking the assistant](#asking-the-assistant)
- [Sharing and deleting](#sharing-and-deleting)
- [How it works](#how-it-works)

## Collections

Papers are kept in collections, e.g. "Reinforcement learning", listed under **My papers**: a tab beside **My
courses**, where the app opens, and an item of the app's menu. A collection is created there with a name, which becomes
its id in links (`reinforcement-learning`), and is shown by the name as it was typed; its creator can rename it.

Collections and courses are listed apart: a collection is never among **My courses**, nor a course among **My
papers**. They share one set of names, though: a student can't have a course and a collection called the same.

## Adding a paper

On a collection's page, its owners choose a file and **Add paper**. A paper is a PDF, an EPUB, a Markdown or a text
file; anything else, e.g. a video, is refused.

A paper stays one paper. A PDF or an EPUB is converted to Markdown, as material in a course is (see
[PDFs and EPUBs](../README.md#pdfs-and-epubs)), and read by its own sections, e.g. Abstract, Introduction, Method: from
a PDF's outline if it has one, else from the sizes of its fonts. It is never made into lessons or topics, as **Make
lessons from a document** makes a book in a course. **Download original** gives the file as it was uploaded.

A paper is processed in the background, as material is, and can be opened once it is ready.

## A paper's details

Each paper has a title, authors, a year, a venue and a DOI, shown on its collection's page as, e.g.:

> **Proximal Policy Optimization Algorithms**
> John Schulman, Filip Wolski · 2017 · arXiv · 1707.06347.pdf

When a paper is added, they are filled in from it where they can be
(`backend/src/qubit_notes/conversion/details.py`):

| Detail  | From                                                                                              |
|---------|---------------------------------------------------------------------------------------------------|
| title   | a PDF's or an EPUB's own title; else the text on a PDF's first page in its largest font, if larger than the rest; a Markdown paper's first top-level heading; else the file's name, e.g. "Ppo" for `ppo.pdf` |
| authors | a PDF's or an EPUB's own authors                                                                  |
| year    | an arXiv identifier on a PDF's first two pages, e.g. `arXiv:1707.06347` is of 2017                |
| venue   | "arXiv", where there is an arXiv identifier                                                       |
| DOI     | the first DOI on a PDF's first two pages, e.g. `10.1038/nature14236`                              |

A PDF's own title is ignored when it is no title, e.g. a file's name such as `Microsoft Word - draft3.docx`. What the
paper doesn't tell is left empty: **Details**, beside a paper, lets the collection's owners change any of them. A paper
needs a title; the year is four digits, and the authors are written separated by commas.

## Reading and notes

A paper opens in the reader, as material does, headed by its title and its collection. Its sections are listed
beside it, and notes are taken on its passages, as on any material (see `features/notes.feature`). Owners can edit a
paper's Markdown, which is processed again. A paper has no reading order: there is no previous or next.

## Asking the assistant

The **AI** button opens the assistant, as on material:

- **On a paper**, it answers from that paper alone, citing its sections, even when other papers of the collection say
  more about the question. "Summarise this paper" gives a summary of the whole paper; "summarise this section" of the
  section being read.
- **On the collection**, from its page, it answers from all of the collection's papers, e.g. to compare them, and
  "summarise this collection" summarises them all.

Quizzes and flashcards have no buttons on papers, but the assistant still makes them if asked, as anywhere.

## Sharing and deleting

A collection is shared as a course is (see `features/sharing.feature`): **Members**, on its page, lists who it is
shared with, and its owners share it with classmates as readers or owners. Readers read the papers, take their own
notes and ask the assistant; only owners add and delete papers and change their details.

Only the student who created a collection can delete it, with **Delete collection**: its papers, and everyone's notes,
summaries and conversations on them, go with it.

## How it works

A collection is a course of the platform that the app keeps apart, so sharing, reading, notes, summaries and the
assistant work on it unchanged. Its papers are its material, all in one topic, `papers/papers`, which no one sees; the
assistant on that topic is the assistant on the whole collection. Each paper is marked, in its metadata, with an id of
its own (`paper`), by which the assistant searches that paper alone.

| Where                                                    | What                                                            |
|----------------------------------------------------------|-----------------------------------------------------------------|
| `backend/src/qubit_notes/domain/papers.py`               | collections, papers and their details                           |
| `backend/src/qubit_notes/conversion/details.py`          | the details a paper tells of itself                             |
| `backend/src/qubit_notes/domain/assistant.py`            | answering about a paper from that paper alone                   |
| `backend/src/qubit_notes/api/papers.py`                  | the endpoints below                                             |
| `frontend/src/pages/PapersPage.tsx`                      | **My papers**: the collections                                  |
| `frontend/src/pages/CollectionPage.tsx`                  | a collection: its papers, their details, members, the assistant |
| `frontend/src/components/Reader.tsx`                     | reading a paper, as material                                    |

The app's database keeps which courses are collections (`paper_collections`) and the papers' details
(`paper_details`); the migration `0013` adds them.

The endpoints, under `/api/papers`:

| Request                                                        | Does                                              |
|----------------------------------------------------------------|---------------------------------------------------|
| `GET /collections`                                             | the student's collections, and those shared with them |
| `POST /collections` `{name, title}`                            | creates a collection                              |
| `GET /collections/{id}`                                        | a collection                                      |
| `PUT /collections/{id}/title` `{title}`                        | renames it; only its creator can                  |
| `DELETE /collections/{id}`                                     | deletes it and its papers; only its creator can   |
| `GET`, `PUT /collections/{id}/members`, `DELETE …/members/{student}` | who it is shared with, as a course's members |
| `GET /collections/{id}/papers`                                 | its papers, with their details, by title          |
| `POST /collections/{id}/papers` (a file)                       | adds a paper, processed in the background         |
| `GET /collections/{id}/papers/{document}`                      | a paper                                           |
| `PUT /collections/{id}/papers/{document}/details`              | changes its details; only owners can              |
| `DELETE /collections/{id}/papers/{document}`                   | deletes it; only owners can                       |

A paper is read, noted and asked about through the material endpoints, with its collection's id as the course's and
its material's `document_id`, e.g. `GET /api/courses/{id}/materials/{document}`.
