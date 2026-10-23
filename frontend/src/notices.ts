// a message for the page the student is sent to next, e.g. that the material they saved has broken references
let pending: string | null = null

export function leaveNotice(message: string): void {
  pending = message
}

/** the message left for this page, once */
export function takeNotice(): string | null {
  const message = pending
  pending = null
  return message
}

/** what the student is told of the broken references of a material they saved */
export function brokenReferences(filename: string, broken: string[]): string | null {
  if (!broken.length) return null
  const which = broken.join(', ')
  return broken.length === 1
    ? `${filename} was saved, but the reference ${which} is broken: the course has nothing by that name`
    : `${filename} was saved, but the references ${which} are broken: the course has nothing by those names`
}
