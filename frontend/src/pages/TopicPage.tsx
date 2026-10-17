import type { StudyApi } from '../api'
import { StudyTools } from '../components/StudyTools'
import { href } from '../router'

type Props = { api: StudyApi; courseId: string; subject: string; topic: string }

/** Summaries and quizzes of every text of a topic. */
export function TopicPage({ api, courseId, subject, topic }: Props) {
  return (
    <section className="topic-study" aria-labelledby="topic-study-title">
      <header className="page-header">
        <a className="link" href={href({ page: 'course', courseId })}>
          ← Back to the course
        </a>
        <h2 id="topic-study-title">
          {subject} › {topic}
        </h2>
        <span className="note">every text of the topic</span>
      </header>
      <StudyTools
        key={`${courseId}/${subject}/${topic}`}
        api={api}
        scope={{ course_id: courseId, subject, topic }}
        label={`${subject} › ${topic}`}
      />
    </section>
  )
}
