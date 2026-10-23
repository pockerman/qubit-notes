import type { Material } from './api'

export const STATUS_LABEL: Record<Material['status'], string> = {
  pending: 'processing',
  running: 'processing',
  completed: 'ready',
  failed: 'failed',
}

/** a topic's status from its materials': processing while any is, failed if any failed, else ready */
export function topicStatus(materials: Material[]): { label: string; bad: boolean } {
  if (!materials.length) return { label: 'no material', bad: false }
  if (materials.some((m) => m.status === 'pending' || m.status === 'running'))
    return { label: 'processing', bad: false }
  if (materials.some((m) => m.status === 'failed')) return { label: 'failed', bad: true }
  const count = materials.length === 1 ? '1 material' : `${materials.length} materials`
  return { label: `ready · ${count}`, bad: false }
}
