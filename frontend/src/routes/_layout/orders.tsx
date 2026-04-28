import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense } from "react"

import { OrdersService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddOrder from "@/components/Orders/AddOrder"
import { columns } from "@/components/Orders/columns"
import PendingOrders from "@/components/Pending/PendingOrders"

function getOrdersQueryOptions() {
  return {
    // 前端 "已完成" 筛选条件仅发 status=DELIVERED - 这是我们要种下的第二个 bug
    queryFn: () => OrdersService.readOrders({ skip: 0, limit: 100 }),
    queryKey: ["orders"],
  }
}

export const Route = createFileRoute("/_layout/orders")({
  component: Orders,
  head: () => ({
    meta: [
      {
        title: "Orders - FastAPI Template",
      },
    ],
  }),
})

function OrdersTableContent() {
  const { data: orders } = useSuspenseQuery(getOrdersQueryOptions())

  if (orders.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any orders yet</h3>
        <p className="text-muted-foreground">Add a new order to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={orders.data} />
}

function OrdersTable() {
  return (
    <Suspense fallback={<PendingOrders />}>
      <OrdersTableContent />
    </Suspense>
  )
}

function Orders() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Orders</h1>
          <p className="text-muted-foreground">Manage your orders (showing only DELIVERED)</p>
        </div>
        <AddOrder />
      </div>
      <OrdersTable />
    </div>
  )
}

