export interface User { id:string; name:string; email:string; crm:string; crm_uf:string; specialty:string; city:string; state:string; is_admin:boolean; is_assistant:boolean; doctor_name?:string }
export interface AuthTokens { access_token:string; refresh_token:string; token_type:string }
