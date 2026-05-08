import { useMemo, useState } from "react";
import { format } from "date-fns";
import { Copy, KeyRound, Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import {
  useApiKeys,
  useCreateApiKey,
  useDeleteApiKey,
  useRenameApiKey,
} from "@/hooks/use-api-keys";
import type { ApiKeyItem, CreatedApiKey } from "@/services/types/api-keys";
import { Button } from "../ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../ui/alert-dialog";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { Input } from "../ui/input";
import { Label } from "../ui/label";

function formatDate(value?: string | null) {
  if (!value) return "Never";
  return format(new Date(value), "MMM d, yyyy");
}

export function ApiKeysSection() {
  const { data = [], isLoading } = useApiKeys();
  const createMutation = useCreateApiKey();
  const renameMutation = useRenameApiKey();
  const deleteMutation = useDeleteApiKey();

  const [createOpen, setCreateOpen] = useState(false);
  const [renameTarget, setRenameTarget] = useState<ApiKeyItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<ApiKeyItem | null>(null);
  const [name, setName] = useState("");
  const [createdKey, setCreatedKey] = useState<CreatedApiKey | null>(null);

  const isCreateMode = useMemo(() => createdKey === null, [createdKey]);

  async function handleCreate() {
    if (!name.trim()) {
      toast.error("Alias is required");
      return;
    }
    const created = await createMutation.mutateAsync({ name: name.trim() });
    setCreatedKey(created);
  }

  async function handleRename() {
    if (!renameTarget) return;
    if (!name.trim()) {
      toast.error("Alias is required");
      return;
    }
    await renameMutation.mutateAsync({
      id: renameTarget.id,
      data: { name: name.trim() },
    });
    setRenameTarget(null);
    setName("");
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    await deleteMutation.mutateAsync(deleteTarget.id);
    setDeleteTarget(null);
  }

  async function handleCopy() {
    if (!createdKey) return;
    await navigator.clipboard.writeText(createdKey.key);
    toast.success("API key copied");
  }

  function resetCreateDialog(open: boolean) {
    setCreateOpen(open);
    if (!open) {
      setCreatedKey(null);
      setName("");
    }
  }

  function openRename(item: ApiKeyItem) {
    setRenameTarget(item);
    setName(item.name);
  }

  return (
    <div className="rounded-xl bg-card p-6 shadow-card">
      <div className="mb-4 flex items-center gap-1.5">
        <KeyRound className="h-4 w-4 text-muted-foreground" />
        <h2 className="text-sm font-semibold text-foreground">API Keys</h2>
        <Button
          size="sm"
          className="ml-auto gap-1.5"
          onClick={() => setCreateOpen(true)}
        >
          <Plus className="h-3.5 w-3.5" />
          Create API Key
        </Button>
      </div>

      <p className="mb-4 text-sm text-muted-foreground">
        Generate API keys for local MCP clients. Keys are shown only once after
        creation.
      </p>

      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="bg-muted/40">
            <tr>
              <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                Alias
              </th>
              <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                Secret Key
              </th>
              <th className="hidden px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground md:table-cell">
                Created
              </th>
              <th className="hidden px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground lg:table-cell">
                Last Used
              </th>
              <th className="px-3 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-3 py-8 text-center text-muted-foreground"
                >
                  Loading API keys...
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-3 py-8 text-center text-muted-foreground"
                >
                  No API keys created yet.
                </td>
              </tr>
            ) : (
              data.map((item) => (
                <tr key={item.id} className="border-t border-border">
                  <td className="px-3 py-3 font-medium text-foreground">
                    {item.name}
                  </td>
                  <td className="px-3 py-3 font-mono text-xs text-muted-foreground">
                    {item.masked_key}
                  </td>
                  <td className="hidden px-3 py-3 text-muted-foreground md:table-cell">
                    {formatDate(item.created_at)}
                  </td>
                  <td className="hidden px-3 py-3 text-muted-foreground lg:table-cell">
                    {formatDate(item.last_used_at)}
                  </td>
                  <td className="px-3 py-3">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="gap-1.5"
                        onClick={() => openRename(item)}
                      >
                        <Pencil className="h-3.5 w-3.5" />
                        Rename
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="gap-1.5 text-destructive hover:text-destructive"
                        onClick={() => setDeleteTarget(item)}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Delete
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <Dialog open={createOpen} onOpenChange={resetCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {isCreateMode ? "Create API Key" : "Save this API key now"}
            </DialogTitle>
            <DialogDescription>
              {isCreateMode
                ? "Create an alias so you can identify this key later."
                : "This is the only time Applika will show the full API key."}
            </DialogDescription>
          </DialogHeader>

          {isCreateMode ? (
            <div className="space-y-2">
              <Label htmlFor="api-key-name">Alias</Label>
              <Input
                id="api-key-name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Local MCP"
              />
            </div>
          ) : (
            <div className="space-y-3">
              <div className="rounded-lg border border-border bg-muted/30 p-3">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Secret key
                </p>
                <code className="break-all text-sm text-foreground">
                  {createdKey?.key}
                </code>
              </div>
              <p className="text-sm text-muted-foreground">
                Store this key securely. You will only see the full value once.
              </p>
            </div>
          )}

          <DialogFooter>
            {isCreateMode ? (
              <>
                <Button
                  variant="outline"
                  onClick={() => resetCreateDialog(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreate}
                  disabled={createMutation.isPending}
                >
                  Create
                </Button>
              </>
            ) : (
              <>
                <Button variant="outline" onClick={handleCopy}>
                  <Copy className="mr-1.5 h-3.5 w-3.5" />
                  Copy
                </Button>
                <Button onClick={() => resetCreateDialog(false)}>Done</Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={renameTarget !== null}
        onOpenChange={(open) => {
          if (!open) {
            setRenameTarget(null);
            setName("");
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename API Key</DialogTitle>
            <DialogDescription>
              Update the alias used to identify this key.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="rename-api-key">Alias</Label>
            <Input
              id="rename-api-key"
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setRenameTarget(null);
                setName("");
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleRename} disabled={renameMutation.isPending}>
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete API key?</AlertDialogTitle>
            <AlertDialogDescription>
              This revokes the key immediately. Any MCP client using it will
              stop working until you configure a new key.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteMutation.isPending}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
