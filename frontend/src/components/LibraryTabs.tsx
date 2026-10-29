import { href } from '../router'

/** "My courses" and "My papers", one tab each, above both: a student lands on their courses. */
export function LibraryTabs({ current }: { current: 'courses' | 'papers' }) {
  return (
    <nav className="library-tabs" aria-label="My library">
      <a href={href({ page: 'courses' })} aria-current={current === 'courses' ? 'page' : undefined}>
        My courses
      </a>
      <a href={href({ page: 'papers' })} aria-current={current === 'papers' ? 'page' : undefined}>
        My papers
      </a>
    </nav>
  )
}
