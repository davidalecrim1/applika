import { api } from "@/lib/api-client";
import type { IApiKeyService } from "@/services/interfaces/i-api-key-service";
import type {
  ApiKeyItem,
  CreateApiKeyPayload,
  CreatedApiKey,
  RenameApiKeyPayload,
} from "@/services/types/api-keys";

export class ApiKeyService implements IApiKeyService {
  listApiKeys(): Promise<ApiKeyItem[]> {
    return api.get<ApiKeyItem[]>("/users/me/api-keys").then((r) => r.data);
  }

  createApiKey(data: CreateApiKeyPayload): Promise<CreatedApiKey> {
    return api
      .post<CreatedApiKey>("/users/me/api-keys", data)
      .then((r) => r.data);
  }

  renameApiKey(
    id: string,
    data: RenameApiKeyPayload,
  ): Promise<ApiKeyItem> {
    return api
      .patch<ApiKeyItem>(`/users/me/api-keys/${id}`, data)
      .then((r) => r.data);
  }

  deleteApiKey(id: string): Promise<void> {
    return api.delete(`/users/me/api-keys/${id}`).then(() => undefined);
  }
}
