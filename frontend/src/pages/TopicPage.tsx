import { useState } from 'react'
import type { StudyApi } from '../api'
import { Assistant } from '../components/Assistant'
import { href } from '../router'

type Props = { api: StudyApi; courseId: string; subject: string; topic: string }

/** Studying every text of a topic with the assistant. */
export function TopicPage({ api, courseId, subject, topic }: Props) {
  const [assistant, setAssistant] = useState(false)
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
        <div role="group" aria-label="Topic actions" className="reader-actions">
          <button type="button" aria-pressed={assistant} onClick={() => setAssistant(!assistant)}>
            AI
          </button>
        </div>
      </header>
      {assistant ? (
        <Assistant
          key={`${courseId}/${subject}/${topic}`}
          api={api}
          where={{ course_id: courseId, subject, topic }}
          label={`${subject} › ${topic}`}
          onClose={() => setAssistant(false)}
        />
      ) : (
        <p className="note">Open the assistant to ask about the topic, or for a summary or a quiz of it.</p>
      )}
    </section>
  )
}
