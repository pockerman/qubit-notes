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
