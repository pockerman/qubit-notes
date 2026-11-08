import { useState } from 'react'
import type { Tool } from './api'

/** A language whose programs can be run beside the notes, by the tool of the same id: Go, Python, C++ or SQL. */
export type Language = {
  id: string
  name: string
  // what its code blocks are marked with
  fences: string[]
  // what its editor starts with
  starter: string
  // what Tab puts in
  indent: string
}

export const LANGUAGES: Language[] = [
  {
    id: 'go',
    name: 'Go',
    fences: ['go', 'golang'],
    starter: 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("hello, world")\n}\n',
    indent: '\t',
  },
  {
    id: 'python',
    name: 'Python',
    fences: ['python', 'py', 'python3'],
    starter: 'print("hello, world")\n',
    indent: '    ',
  },
  {
    id: 'cpp',
    name: 'C++',
    fences: ['cpp', 'c++', 'cxx', 'cc', 'hpp'],
    starter: '#include <iostream>\n\nint main() {\n    std::cout << "hello, world" << std::endl;\n}\n',
    indent: '    ',
  },
  {
    // SQLite, on a database of its own each run
    id: 'sql',
    name: 'SQL',
    fences: ['sql', 'sqlite'],
    starter:
      "CREATE TABLE people (name TEXT, age INTEGER);\nINSERT INTO people VALUES ('Ada', 36), ('Alan', 41);\n\n" +
      'SELECT name, age FROM people WHERE age > 40;\n',
    indent: '  ',
  },
]

/** The editors of the languages a subject's tools run, which of them is open, and what is in each, which stays while
 * the material is open. */
export function useProgramEditors(tools: Tool[]) {
  const languages = LANGUAGES.filter((language) => tools.some((tool) => tool.id === language.id))
  // the id of the language whose editor is open
  const [open, setOpen] = useState<string | null>(null)
  const [sources, setSources] = useState<Record<string, string>>(() =>
    Object.fromEntries(LANGUAGES.map((language) => [language.id, language.starter])),
  )
  const language = languages.find((l) => l.id === open) ?? null
  return {
    languages,
    // the language whose editor is open, if its tool is still attached
    language,
    source: language ? sources[language.id] : '',
    setSource: (source: string) => language && setSources((all) => ({ ...all, [language.id]: source })),
    // opens or closes a language's editor
    toggle: (id: string) => setOpen(open === id ? null : id),
    close: () => setOpen(null),
    // puts a code block's code in its language's editor, and opens it
    openCode: (language: Language, code: string) => {
      setSources((all) => ({ ...all, [language.id]: code }))
      setOpen(language.id)
    },
  }
}
