import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { OrderPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteOrder from "../Orders/DeleteOrder"
import EditOrder from "../Orders/EditOrder"

interface OrderActionsMenuProps {
  order: OrderPublic
}

export const OrderActionsMenu = ({ order }: OrderActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditOrder order={order} onSuccess={() => setOpen(false)} />
        <DeleteOrder id={order.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

