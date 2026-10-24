/**
 * A name as courses, subjects and topics are stored: lowercase words joined by single hyphens, e.g.
 * "Distributed Systems Design" as "distributed-systems-design". Accents are dropped and other characters separate
 * words; a name with no letters or digits becomes "".
 */
export function slug(name: string): string {
  return name
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

/**
 * The name of a subject or topic that wasn't given one: its id, with spaces for hyphens and a capital first letter,
 * e.g. "Finite elements" for finite-elements.
 */
export function named(id: string): string {
  const words = id.replace(/-/g, ' ')
  return words.charAt(0).toUpperCase() + words.slice(1)
}

/** What a course's subjects and topics are called, by their ids, from its topics. */
export type Names = {
  subject: (subject: string) => string
  topic: (subject: string, topic: string) => string
}

export function namesOf(topics: { subject: string; topic: string; subject_name: string; name: string }[]): Names {
  const subjects = new Map(topics.map((t) => [t.subject, t.subject_name]))
  const of = new Map(topics.map((t) => [`${t.subject}/${t.topic}`, t.name]))
  return {
    subject: (subject) => subjects.get(subject) || named(subject),
    topic: (subject, topic) => of.get(`${subject}/${topic}`) || named(topic),
  }
}
