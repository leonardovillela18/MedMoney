export type TaxStatus='Estimado'|'Reservado'|'Pago'|'Ignorado'
export type TaxEstimation={id:string;base_calculo:number;percentual:number;valor_estimado:number;tipo:string;competencia:string;status:TaxStatus;observacoes?:string}
export type TaxDashboard={estimated_month:number;reserved_total:number;not_reserved:number;estimated_net_profit:number;gross_month:number;coverage:number;series:{month:string;gross:number;tax:number;net:number}[];insights:string[];disclaimer:string}
export type TaxPageData={items:TaxEstimation[];total:number;page:number;page_size:number}
export type Simulation={receita:number;percentual:number;reserva_sugerida:number;lucro_liquido_estimado:number;disclaimer:string}
