<template>
  <div class="simulation-canvas">
    <canvas
      ref="canvasRef"
      :width="canvasWidth"
      :height="canvasHeight"
      @click="handleCanvasClick"
      @mousemove="handleMouseMove"
      @mouseleave="hideTooltip"
    ></canvas>
    <div
      v-if="tooltip.visible"
      class="canvas-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div class="tooltip-title">{{ tooltip.title }}</div>
      <div class="tooltip-content" v-html="tooltip.content"></div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from "vue";

export default {
  name: "SimulationCanvas",
  props: {
    gridSize: {
      type: Number,
      default: 15,
    },
    vehicles: {
      type: Array,
      default: () => [],
    },
    orders: {
      type: Array,
      default: () => [],
    },
    obstacles: {
      type: Array,
      default: () => [],
    },
    chargingStations: {
      type: Array,
      default: () => [],
    },
  },
  emits: ["cell-click"],
  setup(props, { emit }) {
    const canvasRef = ref(null);
    const cellSize = 65; // 继续增大：60 → 65
    const canvasWidth = ref(975); // 15 * 65 = 975
    const canvasHeight = ref(975);
    const tooltip = ref({
      visible: false,
      x: 0,
      y: 0,
      title: "",
      content: "",
    });

    const drawGrid = (ctx) => {
      ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value);

      // Draw grid lines
      ctx.strokeStyle = "#e0e0e0";
      ctx.lineWidth = 1;

      for (let i = 0; i <= props.gridSize; i++) {
        // Vertical lines
        ctx.beginPath();
        ctx.moveTo(i * cellSize, 0);
        ctx.lineTo(i * cellSize, props.gridSize * cellSize);
        ctx.stroke();

        // Horizontal lines
        ctx.beginPath();
        ctx.moveTo(0, i * cellSize);
        ctx.lineTo(props.gridSize * cellSize, i * cellSize);
        ctx.stroke();
      }

      // Draw obstacles
      ctx.fillStyle = "#424242";
      props.obstacles.forEach(([x, y]) => {
        ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
      });

      // Draw charging stations (⚡ icon)
      if (props.chargingStations && props.chargingStations.length > 0) {
        props.chargingStations.forEach((station) => {
          const pos = station.position || station;
          const x = pos[0];
          const y = pos[1];

          // Background circle
          const utilization = station.utilization_rate || 0;
          ctx.fillStyle =
            utilization >= 0.8
              ? "#FF5252"
              : utilization >= 0.5
              ? "#FFC107"
              : "#4CAF50";
          ctx.beginPath();
          ctx.arc(
            x * cellSize + cellSize / 2,
            y * cellSize + cellSize / 2,
            cellSize / 2.5,
            0,
            2 * Math.PI
          );
          ctx.fill();

          // Lightning bolt (⚡)
          ctx.fillStyle = "#FFFFFF";
          ctx.font = "bold 32px Arial"; // 增大字体：24px → 32px
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(
            "⚡",
            x * cellSize + cellSize / 2,
            y * cellSize + cellSize / 2
          );
        });
      }

      // Draw orders
      props.orders.forEach((order) => {
        if (order.pickup) {
          // 绘制取货点方块
          ctx.fillStyle = "#4CAF50";
          ctx.fillRect(
            order.pickup[0] * cellSize + 5,
            order.pickup[1] * cellSize + 5,
            cellSize - 10,
            cellSize - 10
          );

          // 绘制订单ID文字
          ctx.fillStyle = "#FFFFFF";
          ctx.font = "bold 14px Arial";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(
            order.id.toString(),
            order.pickup[0] * cellSize + cellSize / 2,
            order.pickup[1] * cellSize + cellSize / 2
          );
        }
        if (order.delivery) {
          // 绘制送货点方块
          ctx.fillStyle = "#2196F3";
          ctx.fillRect(
            order.delivery[0] * cellSize + 5,
            order.delivery[1] * cellSize + 5,
            cellSize - 10,
            cellSize - 10
          );

          // 绘制订单ID文字
          ctx.fillStyle = "#FFFFFF";
          ctx.font = "bold 14px Arial";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(
            order.id.toString(),
            order.delivery[0] * cellSize + cellSize / 2,
            order.delivery[1] * cellSize + cellSize / 2
          );
        }
      });

      // Draw vehicles (with battery-based colors)
      props.vehicles.forEach((vehicle) => {
        if (vehicle.position) {
          const battery = vehicle.battery || 100;

          // Color based on battery level
          let color;
          if (battery < 10) {
            color = "#F44336"; // Red (critical)
          } else if (battery < 30) {
            color = "#FF5722"; // Deep orange (low)
          } else if (battery < 50) {
            color = "#FFC107"; // Amber (medium)
          } else {
            color = "#4CAF50"; // Green (good)
          }

          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(
            vehicle.position[0] * cellSize + cellSize / 2,
            vehicle.position[1] * cellSize + cellSize / 2,
            cellSize / 3,
            0,
            2 * Math.PI
          );
          ctx.fill();

          // Add white border for better visibility
          ctx.strokeStyle = "#FFFFFF";
          ctx.lineWidth = 2;
          ctx.stroke();

          // Add battery indicator (small text)
          ctx.fillStyle = "#FFFFFF";
          ctx.font = "bold 12px Arial"; // 增大字体：10px → 12px
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(
            Math.floor(battery) + "%",
            vehicle.position[0] * cellSize + cellSize / 2,
            vehicle.position[1] * cellSize + cellSize / 2
          );
        }
      });
    };

    const handleCanvasClick = (event) => {
      const rect = canvasRef.value.getBoundingClientRect();
      const x = Math.floor((event.clientX - rect.left) / cellSize);
      const y = Math.floor((event.clientY - rect.top) / cellSize);
      emit("cell-click", { x, y });
    };

    const handleMouseMove = (event) => {
      const rect = canvasRef.value.getBoundingClientRect();
      const x = Math.floor((event.clientX - rect.left) / cellSize);
      const y = Math.floor((event.clientY - rect.top) / cellSize);

      // 智能定位tooltip，避免超出边界
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;
      const tooltipWidth = 200; // tooltip大致宽度
      const tooltipHeight = 120; // tooltip大致高度

      let tooltipX = mouseX + 10;
      let tooltipY = mouseY + 10;

      // 如果超出右边界，放在鼠标左侧
      if (tooltipX + tooltipWidth > canvasWidth.value) {
        tooltipX = mouseX - tooltipWidth - 10;
      }

      // 如果超出下边界，放在鼠标上方
      if (tooltipY + tooltipHeight > canvasHeight.value) {
        tooltipY = mouseY - tooltipHeight - 10;
      }

      // 确保不会超出左边界和上边界
      tooltipX = Math.max(5, tooltipX);
      tooltipY = Math.max(5, tooltipY);

      // Check for charging station
      const station = props.chargingStations?.find((s) => {
        const pos = s.position || s;
        return pos[0] === x && pos[1] === y;
      });

      if (station) {
        const available = station.available_slots || 0;
        const capacity = station.capacity || 2;
        const queueLength = station.queue_length || 0;
        const utilization = ((station.utilization_rate || 0) * 100).toFixed(0);

        tooltip.value = {
          visible: true,
          x: tooltipX,
          y: tooltipY,
          title: `⚡ 充电站 #${station.id || 0}`,
          content: `
            <div><strong>可用充电位:</strong> ${available}/${capacity}</div>
            <div><strong>使用率:</strong> ${utilization}%</div>
            <div><strong>排队车辆:</strong> ${queueLength}辆</div>
            ${
              queueLength > 0
                ? `<div style="color: #FFC107;">等待队列: ${
                    station.waiting_queue?.join(", ") || ""
                  }</div>`
                : ""
            }
          `,
        };
        return;
      }

      // Check for vehicle
      const vehicle = props.vehicles?.find(
        (v) => v.position && v.position[0] === x && v.position[1] === y
      );

      if (vehicle) {
        const battery = vehicle.battery || 100;
        const state = vehicle.state || "Unknown";
        const orderId = vehicle.current_order || "None";

        tooltip.value = {
          visible: true,
          x: tooltipX,
          y: tooltipY,
          title: `🚗 车辆 #${vehicle.id}`,
          content: `
            <div><strong>电量:</strong> <span style="color: ${
              battery < 30 ? "#FF5722" : "#4CAF50"
            }">${battery.toFixed(1)}%</span></div>
            <div><strong>状态:</strong> ${state}</div>
            <div><strong>当前订单:</strong> ${orderId}</div>
          `,
        };
        return;
      }

      // Hide tooltip if not hovering over anything
      tooltip.value.visible = false;
    };

    const hideTooltip = () => {
      tooltip.value.visible = false;
    };

    onMounted(() => {
      canvasWidth.value = props.gridSize * cellSize;
      canvasHeight.value = props.gridSize * cellSize;

      const ctx = canvasRef.value.getContext("2d");
      drawGrid(ctx);
    });

    watch(
      () => [
        props.vehicles,
        props.orders,
        props.obstacles,
        props.chargingStations,
        props.gridSize,
      ],
      () => {
        if (canvasRef.value) {
          const ctx = canvasRef.value.getContext("2d");
          drawGrid(ctx);
        }
      },
      { deep: true }
    );

    return {
      canvasRef,
      canvasWidth,
      canvasHeight,
      handleCanvasClick,
      handleMouseMove,
      hideTooltip,
      tooltip,
    };
  },
};
</script>

<style scoped>
.simulation-canvas {
  display: inline-block;
  border: 2px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

canvas {
  display: block;
  cursor: crosshair;
}

.canvas-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.85);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  z-index: 1000;
  min-width: 180px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.tooltip-title {
  font-weight: bold;
  font-size: 13px;
  margin-bottom: 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.tooltip-content {
  line-height: 1.6;
}

.tooltip-content div {
  margin: 2px 0;
}
</style>
