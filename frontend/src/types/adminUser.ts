export type AdminUser={id:string;name:string;email:string;crm:string;crm_uf:string;cnpj:string;phone:string;city:string;state:string;specialty:string;active:boolean;created_at:string;role:string}
export type AdminUserPayload=Omit<AdminUser,'id'|'active'|'created_at'|'role'>&{password?:string}
