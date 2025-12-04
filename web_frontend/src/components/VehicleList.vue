<template>
  <div class="vehicle-list">
    <el-table :data="vehicles" height="400" @row-click="handleRowClick">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="state" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStateType(scope.row.state)" size="small">
            {{ translateState(scope.row.state) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="position" label="位置" width="100">
        <template #default="scope">
          {{
            scope.row.position
              ? `(${scope.row.position[0]}, ${scope.row.position[1]})`
              : "-"
          }}
        </template>
      </el-table-column>
      <el-table-column prop="battery" label="电量" width="100">
        <template #default="scope">
          <el-progress
            :percentage="scope.row.battery || 0"
            :color="getBatteryColor(scope.row.battery)"
            :stroke-width="8"
          />
        </template>
      </el-table-column>
      <el-table-column label="任务">
        <template #default="scope">
          {{ scope.row.current_order || "-" }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: "VehicleList",
  props: {
    vehicles: {
      type: Array,
      default: () => [],
    },
  },
  emits: ["vehicle-select"],
  setup(props, { emit }) {
    const getStateType = (state) => {
      const typeMap = {
        Idle: "info",
        MovingToPickup: "warning",
        PickingUp: "primary",
        MovingToDelivery: "warning",
        Delivering: "success",
        Charging: "danger",
      };
      return typeMap[state] || "info";
    };

    const translateState = (state) => {
      const stateMap = {
        Idle: "空闲",
        MovingToPickup: "前往取货",
        PickingUp: "取货中",
        MovingToDelivery: "配送中",
        Delivering: "送达中",
        Charging: "充电中",
      };
      return stateMap[state] || state;
    };

    const getBatteryColor = (battery) => {
      if (battery > 60) return "#67C23A";
      if (battery > 30) return "#E6A23C";
      return "#F56C6C";
    };

    const handleRowClick = (row) => {
      emit("vehicle-select", row.id);
    };

    return {
      getStateType,
      translateState,
      getBatteryColor,
      handleRowClick,
    };
  },
};
</script>

<style scoped>
.vehicle-list {
  width: 100%;
}
</style>
