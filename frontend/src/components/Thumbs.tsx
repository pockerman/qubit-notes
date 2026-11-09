import type { Rating } from '../api'

type Props = {
  rating: Rating | null
  // the thumb chosen; the one pressed chosen again is null, which takes the rating back
  onRate: (rating: Rating | null) => void
}

/** A thumbs up and a thumbs down of a reply of the AI: the one chosen stays pressed (features/rating_answers.feature). */
export function Thumbs({ rating, onRate }: Props) {
  const thumb = (which: Rating, label: string, title: string, icon: string) => (
    <button
      type="button"
      className="icon thumb"
      aria-label={label}
      title={title}
      aria-pressed={rating === which}
      onClick={() => onRate(rating === which ? null : which)}
    >
      {icon}
    </button>
  )
  return (
    <>
      {thumb('up', 'Thumbs up', 'Good reply', '👍')}
      {thumb('down', 'Thumbs down', 'Bad reply', '👎')}
    </>
  )
}
