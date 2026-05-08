import type {
  ApiKeyItem,
  CreateApiKeyPayload,
  CreatedApiKey,
  RenameApiKeyPayload,
} from "@/services/types/api-keys";

export interface IApiKeyService {
  listApiKeys(): Promise<ApiKeyItem[]>;
  createApiKey(data: CreateApiKeyPayload): Promise<CreatedApiKey>;
  renameApiKey(
    id: string,
    data: RenameApiKeyPayload,
  ): Promise<ApiKeyItem>;
  deleteApiKey(id: string): Promise<void>;
}
