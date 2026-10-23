# References between topics

A Markdown material can refer to another part of its course: a topic, a material, or a section of a material.
In the reader each reference is a link to what it refers to, and each topic lists the materials that mention it.
The behaviour is specified in [`features/references.feature`](../features/references.feature) and
[`features/ui_references.feature`](../features/ui_references.feature).

- [Writing a reference](#writing-a-reference)
- [Labels](#labels)
- [Following a reference](#following-a-reference)
- [Broken references](#broken-references)
- [Mentions](#mentions)
- [Downloads of converted PDFs and EPUBs](#downloads-of-converted-pdfs-and-epubs)
- [How it works](#how-it-works)

## Writing a reference

A reference is a path in double brackets. The path is made of the names the course uses: the subject's and the
topic's (lowercase words joined by hyphens), and the material's file name.

| To refer to                  | Write                                                   |
|------------------------------|---------------------------------------------------------|
| a topic                      | `[[numerical-methods/finite-elements]]`                 |
| a material in a topic        | `[[numerical-methods/finite-elements/fem-notes.md]]`    |
| a section of a material      | `[[numerical-methods/finite-elements/fem-notes.md#2 Assembly]]` |

For example:

```markdown
# 1 Sparse matrices
The stiffness matrix of [[numerical-methods/finite-elements]] is sparse.
It is assembled as in [[numerical-methods/finite-elements/fem-notes.md#2 Assembly|the assembly]].
```

- **The path always starts at the subject**, even for a topic in the same subject. `[[finite-elements]]` is not a
  reference to anything.
- **A section is named by its heading**, exactly as it is written, without the `#` marks: the heading
  `## 2 Assembly` is the section `2 Assembly`. A PDF converted without an outline has the sections `Page 1`,
  `Page 2` and so on.
- **A material's name is its file name**, as the course lists it, e.g. `lecture-1.pdf` for a converted PDF.
- **References are within one course.** There is no way to refer to another course.
- **Any material can be referred to**, including PDFs and videos, but only Markdown material can contain
  references: written material, uploaded `.md` files, and PDFs and EPUBs (which are converted to Markdown).
- **Text in code is not a reference.** `` `[[a/b]]` `` and a `[[a/b]]` inside a fenced code block are shown as
  written, which is how to write about the syntax itself.

You don't have to type the path. While writing or editing a material, **Add reference** lets you pick a topic, then
optionally one of its materials, then optionally one of that material's sections, and puts the reference where the
cursor is. **How references work**, beside it, shows a summary of this page.

## Labels

A reference is shown as the name of what it refers to: the topic's name, the material's file name, or the section's
heading. To show something else, add a label after a `|`:

| Written                                                                      | Shown as         |
|------------------------------------------------------------------------------|------------------|
| `[[numerical-methods/finite-elements]]`                                      | finite-elements  |
| `[[numerical-methods/finite-elements\|the FEM topic]]`                        | the FEM topic    |
| `[[numerical-methods/finite-elements/fem-notes.md]]`                         | fem-notes.md     |
| `[[numerical-methods/finite-elements/fem-notes.md#2 Assembly]]`              | 2 Assembly       |
| `[[numerical-methods/finite-elements/fem-notes.md#2 Assembly\|the assembly]]` | the assembly     |

A `|` in a Markdown table separates its cells, so a reference with a label inside a table needs it escaped, as in
the table above: `\|`.

## Following a reference

| A reference to | opens                                                         |
|----------------|---------------------------------------------------------------|
| a topic        | the course, scrolled to the topic, which is outlined          |
| a material     | the material in the reader                                    |
| a section      | the material in the reader, at that section                   |

Readers of a shared course follow references as owners do.

## Broken references

A reference is broken when the course has nothing by that name: the topic, the material or the section doesn't
exist, it was mistyped, or the path is incomplete (such as `[[finite-elements]]`). A broken reference is shown
struck through in red, and isn't a link.

When you save a material, it is saved whatever its references, and you are told which of them are broken, e.g.:

> sparse-matrices.md was saved, but the reference [[numerical-methods/finite-element]] is broken: the course has
> nothing by that name

A reference can also break later: when the material it refers to is deleted, or when a section's heading is changed.
It works again as soon as there is something by that name, e.g. when a material with the same name is uploaded to the
same topic.

## Mentions

A topic is mentioned in every material that refers to it, to one of its materials, or to a section of one of them.
On the course page, each topic that is mentioned shows **Mentioned in** and the materials, each a link, with the
topic they are in when it's another one. A material is listed once, however many references it has to the topic.
Mentions follow the materials as they are: a mention goes when its last reference is edited out, or when the
material is deleted.

## Downloads of converted PDFs and EPUBs

A PDF or an EPUB downloaded "as it is now" is laid out anew from its Markdown, outside the course, where a link to the
course wouldn't work. Each reference in it is its label, or the name it would be shown as, as plain text:
`[[numerical-methods/linear-solvers|sparse solvers]]` is "sparse solvers". The original file is downloaded as it was
uploaded.

## How it works

Nothing about references is stored. They are read from each material's Markdown when they are asked for, so they are
never out of date: a reference breaks as soon as what it refers to goes, and a mention goes as soon as its reference
does.

| Where                                                    | What                                                            |
|----------------------------------------------------------|-----------------------------------------------------------------|
| `backend/src/qubit_notes/domain/reference_text.py`       | the syntax: finding references in Markdown outside code, their names and labels, and the text a download shows |
| `backend/src/qubit_notes/domain/references.py`           | what each reference refers to in its course, and each topic's mentions |
| `backend/src/qubit_notes/api/references.py`              | the endpoints below                                             |
| `backend/src/qubit_notes/domain/materials.py`            | the broken references reported when a material is uploaded, written or edited |
| `frontend/src/references.ts`                             | the syntax, as the frontend shows a reference before it knows what it refers to |
| `frontend/src/referenceLinks.tsx`                        | references as links, and resolving the text being written       |
| `frontend/src/components/AddReference.tsx`               | the **Add reference** picker and the **How references work** help |

The endpoints:

| Request                                                    | Answers                                                     |
|------------------------------------------------------------|-------------------------------------------------------------|
| `GET /api/courses/{course_id}/materials/{document_id}/references` | the references of a material, each with what it refers to |
| `POST /api/courses/{course_id}/references` with `{"text": …}`      | the same for text not saved yet, for the editor's preview |
| `GET /api/courses/{course}/mentions`                               | each topic of the course with the materials it is mentioned in |

The upload, write and edit endpoints answer with `broken_references`: the broken references of the saved material, as
written.

A reference resolves to `refers_to`: `topic`, `material`, `section` or `nothing` (broken), with the subject, topic,
material, document id, section heading and section position of what it refers to. A section is found among the
sections the platform read from the material, by its heading, so a material still being processed has no sections
to refer to yet.

The cost of reading references when asked for is that the course page reads every Markdown material of the course
each time it loads, to find the mentions. That's fine for a study course; for courses of hundreds of materials, the
references would be better kept in a table, updated whenever a material is saved or deleted.
