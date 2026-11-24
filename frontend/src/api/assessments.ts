import { api } from './client'
import type { Assessment } from '../types/assessment'

export async function createAssessment(merchantId: string): Promise<Assessment> {
  const { data } = await api.post('/assessments', null, { params: { merchant_id: merchantId } })
  return data
}

export async function submitDecision(
  assessmentId: string,
  decision: string,
  adjustedAmount?: number,
  adjustedDuration?: number,
  comments?: string
): Promise<void> {
  await api.post(`/assessments/${assessmentId}/decision`, {
    assessment_id: assessmentId,
    decision,
    adjusted_amount: adjustedAmount,
    adjusted_duration: adjustedDuration,
    comments,
  })
}