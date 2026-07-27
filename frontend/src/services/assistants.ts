import { api } from './api'
export type Assistant={id:string;name:string;email:string;phone:string;active:boolean;created_at:string}
export type AssistantInput={name:string;email:string;phone:string;password?:string}
export const assistantsService={list:()=>api.get<Assistant[]>('/assistants').then(r=>r.data),create:(data:AssistantInput)=>api.post<Assistant>('/assistants',data).then(r=>r.data),update:(id:string,data:AssistantInput)=>api.put<Assistant>(`/assistants/${id}`,data).then(r=>r.data),status:(id:string,active:boolean)=>api.patch<Assistant>(`/assistants/${id}/status`,null,{params:{active}}).then(r=>r.data)}
