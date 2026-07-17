export type CashflowItem={id:string;data:string;tipo:string;origem:string;origem_id:string;descricao:string;categoria:string;valor:number;saldo_projetado:number;status:string}
export type CashflowProjection={summary:{current_balance:number;forecast_balance:number;month_inflows:number;month_outflows:number;net_result:number;tax_reserve:number;available:number};forecasts:{days:number;balance:number}[];series:{date:string;inflow:number;outflow:number;balance:number}[];insights:string[];alerts:string[]}
export type CashflowPageData={items:CashflowItem[];total:number;page:number;page_size:number}
export type CalendarData=Record<string,{id:string;description:string;value:number;balance:number;status:string}[]>
