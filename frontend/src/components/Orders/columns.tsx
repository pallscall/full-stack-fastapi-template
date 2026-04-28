import type { ColumnDef } from "@tanstack/react-table"
import { Check, Copy } from "lucide-react"

import type { OrderPublic } from "@/client"
import { Button } from "@/components/ui/button"
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard"
import { cn } from "@/lib/utils"
import { OrderActionsMenu } from "./OrderActionsMenu"

function CopyId({ id }: { id: string }) {
  const [copiedText, copy] = useCopyToClipboard()
  const isCopied = copiedText === id

  return (
    <div className="flex items-center gap-1.5 group">
      <span className="font-mono text-xs text-muted-foreground">{id}</span>
      <Button
        variant="ghost"
        size="icon"
        className="size-6 opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={() => copy(id)}
      >
        {isCopied ? (
          <Check className="size-3 text-green-500" />
        ) : (
          <Copy className="size-3" />
        )}
        <span className="sr-only">Copy ID</span>
      </Button>
    </div>
  )
}

export const columns: ColumnDef<OrderPublic>[] = [
  {
    accessorKey: "id",
    header: "ID",
    cell: ({ row }) => <CopyId id={row.original.id} />,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status
      let statusColor = "bg-gray-100 text-gray-800"
      switch (status) {
        case "DELIVERED":
          statusColor = "bg-green-100 text-green-800"
          break
        case "REVIEWED":
          statusColor = "bg-blue-100 text-blue-800"
          break
        case "AUTO_CLOSED":
          statusColor = "bg-purple-100 text-purple-800"
          break
        case "PENDING":
          statusColor = "bg-yellow-100 text-yellow-800"
          break
        case "CANCELLED":
          statusColor = "bg-red-100 text-red-800"
          break
      }
      return (
        <span
          className={cn(
            "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
            statusColor
          )}
        >
          {status}
        </span>
      )
    },
  },
  {
    accessorKey: "createdAt",
    header: "Created At",
    cell: ({ row }) => (
      <span className="text-muted-foreground">
        {row.original.createdAt ? new Date(row.original.createdAt).toLocaleString() : "-"}
      </span>
    ),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <OrderActionsMenu order={row.original} />
      </div>
    ),
  },
]

