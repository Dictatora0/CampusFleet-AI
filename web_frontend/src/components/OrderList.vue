<template>
  <div class="order-list">
    <el-table :data="orders" height="400" @row-click="handleRowClick">
      <el-table-column prop="id" label="订单ID" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)" size="small">
            {{ translateStatus(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="取货点" width="120">
        <template #default="scope">
          {{
            scope.row.pickup
              ? `(${scope.row.pickup[0]}, ${scope.row.pickup[1]})`
              : "-"
          }}
        </template>
      </el-table-column>
      <el-table-column label="送货点" width="120">
        <template #default="scope">
          {{
            scope.row.delivery
              ? `(${scope.row.delivery[0]}, ${scope.row.delivery[1]})`
              : "-"
          }}
        </template>
      </el-table-column>
      <el-table-column label="分配车辆" width="100">
        <template #default="scope">
          {{ scope.row.assigned_vehicle || "-" }}
        </template>
      </el-table-column>
      <el-table-column label="优先级" width="80">
        <template #default="scope">
          <el-rate
            v-model="scope.row.priority"
            disabled
            :max="3"
            size="small"
          />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: "OrderList",
  props: {
    orders: {
      type: Array,
      default: () => [],
    },
  },
  emits: ["order-select"],
  setup(props, { emit }) {
    const getStatusType = (status) => {
      const typeMap = {
        Pending: "warning",
        Assigned: "primary",
        PickedUp: "info",
        Delivered: "success",
        Cancelled: "danger",
      };
      return typeMap[status] || "info";
    };

    const translateStatus = (status) => {
      const statusMap = {
        Pending: "待分配",
        Assigned: "已分配",
        PickedUp: "已取货",
        Delivered: "已送达",
        Cancelled: "已取消",
      };
      return statusMap[status] || status;
    };

    const handleRowClick = (row) => {
      emit("order-select", row.id);
    };

    return {
      getStatusType,
      translateStatus,
      handleRowClick,
    };
  },
};
</script>

<style scoped>
.order-list {
  width: 100%;
}
</style>
