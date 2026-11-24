export interface Merchant {
  merchant_id: string
  activity?: string
  zone?: string
  is_first_time_borrower?: boolean
  activity_age_months?: number
  data_completeness?: number
  monthly_income_mean?: number
  has_inconsistencies?: boolean
  [key: string]: any
}

export interface MerchantListResponse {
  merchants: Merchant[]
  total: number
  page: number
  page_size: number
}