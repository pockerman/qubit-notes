import { useId } from 'react'
import type { SpeechModels } from '../api'
import { chooseSpeechModel } from '../speechModels'

type Props = {
  models: SpeechModels
  chosen: string
  onChoose: (model: string) => void
}

/** OpenAI's speech models, to choose which reads the audio, as the AI is chosen (see ProviderChoice); without the
 * app's OpenAI key, they're shown, but can't be chosen, and say why. */
export function SpeechModelChoice({ models, chosen, onChoose }: Props) {
  const name = useId()
  const why = `${name}-why`
  return (
    <div className="provider-choice speech-model-choice" role="radiogroup" aria-label="Speech model">
      <span aria-hidden="true">Read by</span>
      {models.models.map((model) => (
        <span key={model.id} className={models.available ? 'provider-option' : 'provider-option unavailable'}>
          <label title={model.follows_instructions ? 'Follows how you ask it to speak' : 'Reads it as it does'}>
            {/* not disabled, or it could neither be pointed at nor reached to say why */}
            <input
              type="radio"
              name={name}
              checked={model.id === chosen}
              aria-disabled={!models.available}
              aria-describedby={models.available ? undefined : why}
              onChange={() => {
                if (!models.available) return
                chooseSpeechModel(model.id)
                onChoose(model.id)
              }}
            />
            {model.name}
          </label>
        </span>
      ))}
      {!models.available && (
        <span id={why} role="tooltip" className="provider-tooltip">
          Not available: the app's OpenAI API key is missing
        </span>
      )}
    </div>
  )
}
