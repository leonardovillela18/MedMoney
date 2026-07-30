export type IncomeType='CLT'|'RESIDENCY_GRANT'|'RESEARCH_GRANT'|'ACADEMIC_GRANT'|'PRO_LABORE'|'RENTAL_INCOME'|'PJ_RECURRING'|'OTHER'
export type RecurringIncome={id:string;user_id:string;description:string;income_type:IncomeType;amount:number;frequency:'Semanal'|'Mensal'|'Trimestral'|'Semestral'|'Anual';start_date:string;end_date?:string;day_of_month?:number;next_occurrence_date:string;tax_treatment:'PJ_TAXABLE'|'NON_PJ'|'CUSTOM';tax_reserve_percentage?:number;active:boolean;notes?:string}
export type RecurringIncomePayload=Omit<RecurringIncome,'id'|'user_id'|'next_occurrence_date'>
export type RecurringIncomePage={items:RecurringIncome[];total:number;page:number;page_size:number}
export type IncomeReceivable={id:string;recurring_income_id?:string;expected_value:number;received_value:number;remaining_balance:number;expected_date:string;status:string;tax_treatment:string}
