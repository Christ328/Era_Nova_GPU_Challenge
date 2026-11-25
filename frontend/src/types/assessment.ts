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

export interface Assessment {
  merchant_id: string
  score: number
  ml_score?: number
  business_score?: number
  score_weights?: { ml: number; rules: number }
  risk_level: string
  confidence: string
  data_quality: number
  recommended_amount_min: number
  recommended_amount_max: number
  recommended_duration_months: number
  product_type: string
  human_review_required: boolean
  top_factors: ShapFactor[]
  alerts: Alert[]
  explanation: string
}