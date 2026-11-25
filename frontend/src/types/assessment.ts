export interface ShapFactor {
  feature: string
  label: string
  value: number
  impact: number
  direction: 'positive' | 'negative'
}

export interface Alert {
  severity: 'error' | 'warning' | 'info'
  message: string
  rule_name: string
}

export interface CounterProposal {
  label: string
  amount: number
  duration: number
  score: number
  effort_rate: number
}

export interface Assessment {
  merchant_id: string
  score: number
  ml_score?: number
  business_score?: number
  score_weights?: { ml: number; rules: number }
  risk_level: string
  confidence: string
  data_quality: number
  human_review_required: boolean
  top_factors: ShapFactor[]
  alerts: Alert[]
  explanation: string
  score_max?: number
  decision?: 'ACCEPTED' | 'MANUAL_REVIEW' | 'REFUSED_RISK' | 'REFUSED_REGULATORY'
  teg?: number
  teg_blocked?: boolean
  fraud_detected?: boolean
  counter_proposals?: CounterProposal[]
}
