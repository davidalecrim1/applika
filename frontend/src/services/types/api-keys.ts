export interface ApiKeyItem {
  id: string;
  name: string;
  masked_key: string;
  last4: string;
  created_at: string;
  updated_at?: string | null;
  last_used_at?: string | null;
}

export interface CreatedApiKey extends ApiKeyItem {
  key: string;
}

export interface CreateApiKeyPayload {
  name: string;
}

export interface RenameApiKeyPayload {
  name: string;
}
