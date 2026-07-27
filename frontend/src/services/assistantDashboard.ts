import { api } from './api'
export type AssistantEvent={id:string;type:string;title:string;date:string;time:string;location:string;hours_until:number;urgency:'24h'|'48h'|null}
export type AssistantDashboard={doctor_name:string;summary:{consultations_done:number;surgeries_done:number;consultations_scheduled:number;surgeries_scheduled:number;shifts_scheduled:number};urgent:AssistantEvent[];upcoming:AssistantEvent[]}
export const assistantDashboardService={get:()=>api.get<AssistantDashboard>('/assistant-dashboard').then(r=>r.data)}
