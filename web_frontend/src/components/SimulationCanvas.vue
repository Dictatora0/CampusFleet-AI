<template>
  <div class="simulation-canvas">
    <canvas
      ref="canvasRef"
      :width="canvasWidth"
      :height="canvasHeight"
      @click="handleCanvasClick"
    ></canvas>
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
  },
  emits: ["cell-click"],
  setup(props, { emit }) {
    const canvasRef = ref(null);
    const cellSize = 40;
    const canvasWidth = ref(600);
    const canvasHeight = ref(600);

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

      // Draw orders
      props.orders.forEach((order) => {
        if (order.pickup) {
          ctx.fillStyle = "#4CAF50";
          ctx.fillRect(
            order.pickup[0] * cellSize + 5,
            order.pickup[1] * cellSize + 5,
            cellSize - 10,
            cellSize - 10
          );
        }
        if (order.delivery) {
          ctx.fillStyle = "#2196F3";
          ctx.fillRect(
            order.delivery[0] * cellSize + 5,
            order.delivery[1] * cellSize + 5,
            cellSize - 10,
            cellSize - 10
          );
        }
      });

      // Draw vehicles
      props.vehicles.forEach((vehicle) => {
        if (vehicle.position) {
          ctx.fillStyle = "#FF9800";
          ctx.beginPath();
          ctx.arc(
            vehicle.position[0] * cellSize + cellSize / 2,
            vehicle.position[1] * cellSize + cellSize / 2,
            cellSize / 3,
            0,
            2 * Math.PI
          );
          ctx.fill();
        }
      });
    };

    const handleCanvasClick = (event) => {
      const rect = canvasRef.value.getBoundingClientRect();
      const x = Math.floor((event.clientX - rect.left) / cellSize);
      const y = Math.floor((event.clientY - rect.top) / cellSize);
      emit("cell-click", { x, y });
    };

    onMounted(() => {
      canvasWidth.value = props.gridSize * cellSize;
      canvasHeight.value = props.gridSize * cellSize;

      const ctx = canvasRef.value.getContext("2d");
      drawGrid(ctx);
    });

    watch(
      () => [props.vehicles, props.orders, props.obstacles, props.gridSize],
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
}

canvas {
  display: block;
  cursor: crosshair;
}
</style>
