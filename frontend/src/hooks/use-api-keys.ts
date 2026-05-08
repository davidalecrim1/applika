import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { toast } from "sonner";

import { getApiError } from "@/lib/api-client";
import { services } from "@/services/services";
import type {
  CreateApiKeyPayload,
  RenameApiKeyPayload,
} from "@/services/types/api-keys";

const API_KEYS_QUERY_KEY = ["user", "api-keys"] as const;

export function useApiKeys() {
  return useQuery({
    queryKey: API_KEYS_QUERY_KEY,
    queryFn: () => services.apiKeys.listApiKeys(),
  });
}

export function useCreateApiKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateApiKeyPayload) =>
      services.apiKeys.createApiKey(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: API_KEYS_QUERY_KEY });
      toast.success("API key created");
    },
    onError: (error: AxiosError) => toast.error(getApiError(error)),
  });
}

export function useRenameApiKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: RenameApiKeyPayload;
    }) => services.apiKeys.renameApiKey(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: API_KEYS_QUERY_KEY });
      toast.success("API key renamed");
    },
    onError: (error: AxiosError) => toast.error(getApiError(error)),
  });
}

export function useDeleteApiKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => services.apiKeys.deleteApiKey(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: API_KEYS_QUERY_KEY });
      toast.success("API key deleted");
    },
    onError: (error: AxiosError) => toast.error(getApiError(error)),
  });
}
