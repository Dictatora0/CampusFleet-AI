<template>
  <div class="simulation-view">
    <!-- 控制面板 -->
    <div class="control-panel">
      <el-card class="control-card">
        <template #header>
          <div class="card-header">
            <h3 class="title">
              <el-icon><Operation /></el-icon>
              仿真控制
            </h3>
            <el-tag :type="simulation.isRunning ? 'success' : 'info'">
              {{ simulation.isRunning ? "运行中" : "已停止" }}
            </el-tag>
          </div>
        </template>

        <div class="control-content">
          <!-- 快速配置 -->
          <div class="quick-config mb-16">
            <el-row :gutter="12">
              <el-col :span="8">
                <el-select
                  v-model="selectedPreset"
                  placeholder="选择预设"
                  @change="loadPreset"
                >
                  <el-option label="小规模测试" value="small" />
                  <el-option label="中等规模演示" value="medium" />
                  <el-option label="大规模仿真" value="large" />
                  <el-option label="MAPF协调演示" value="mapfDemo" />
                  <el-option label="VRP拼单演示" value="vrpDemo" />
                </el-select>
              </el-col>
              <el-col :span="8">
                <el-button
                  type="primary"
                  @click="createSimulation"
                  :loading="creating"
                >
                  <el-icon><Plus /></el-icon>
                  创建仿真
                </el-button>
              </el-col>
              <el-col :span="8">
                <el-button
                  type="danger"
                  @click="resetSimulation"
                  :disabled="!hasSimulation"
                >
                  <el-icon><RefreshRight /></el-icon>
                  重置
                </el-button>
              </el-col>
            </el-row>
          </div>

          <!-- 仿真控制按钮 -->
          <div class="simulation-controls mb-16">
            <el-button-group>
              <el-button
                type="success"
                @click="startSimulation"
                :disabled="!hasSimulation || simulation.isRunning"
              >
                <el-icon><VideoPlay /></el-icon>
                启动
              </el-button>
              <el-button
                type="warning"
                @click="stopSimulation"
                :disabled="!hasSimulation || !simulation.isRunning"
              >
                <el-icon><VideoPause /></el-icon>
                停止
              </el-button>
              <el-button
                type="info"
                @click="stepSimulation"
                :disabled="!hasSimulation || simulation.isRunning"
              >
                <el-icon><DArrowRight /></el-icon>
                单步
              </el-button>
            </el-button-group>
          </div>

          <!-- 统计信息 -->
          <div class="statistics">
            <el-row :gutter="12">
              <el-col :span="6">
                <el-statistic title="步数" :value="simulation.step" />
              </el-col>
              <el-col :span="6">
                <el-statistic
                  title="完成订单"
                  :value="simulation.statistics.total_completed_orders || 0"
                />
              </el-col>
              <el-col :span="6">
                <el-statistic title="活跃车辆" :value="activeVehicleCount" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="待处理订单" :value="pendingOrderCount" />
              </el-col>
            </el-row>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主体区域 -->
    <div class="main-content">
      <el-row :gutter="16">
        <!-- 可视化面板 -->
        <el-col :span="16">
          <el-card class="visualization-card">
            <template #header>
              <div class="card-header">
                <h3 class="title">
                  <el-icon><Grid /></el-icon>
                  仿真可视化
                </h3>
                <div class="view-controls">
                  <el-tooltip content="显示路径">
                    <el-button
                      :type="ui.showPath ? 'primary' : ''"
                      size="small"
                      @click="toggleShowPath"
                    >
                      <el-icon><Share /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="显示网格">
                    <el-button
                      :type="ui.showGrid ? 'primary' : ''"
                      size="small"
                      @click="toggleShowGrid"
                    >
                      <el-icon><Grid /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </template>

            <SimulationCanvas
              :simulation-data="simulation"
              :ui-config="ui"
              @vehicle-click="selectVehicle"
              @grid-click="onGridClick"
            />
          </el-card>
        </el-col>

        <!-- 信息面板 -->
        <el-col :span="8">
          <!-- 车辆信息 -->
          <el-card class="info-card mb-16">
            <template #header>
              <div class="card-header">
                <h3 class="title">
                  <el-icon><TruckFilled /></el-icon>
                  车辆状态
                </h3>
              </div>
            </template>

            <VehicleList
              :vehicles="simulation.vehicles"
              :selected-vehicle="ui.selectedVehicle"
              @select-vehicle="selectVehicle"
            />
          </el-card>

          <!-- 订单信息 -->
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <h3 class="title">
                  <el-icon><List /></el-icon>
                  订单管理
                </h3>
                <el-button
                  type="primary"
                  size="small"
                  @click="showOrderDialog = true"
                >
                  <el-icon><Plus /></el-icon>
                  添加
                </el-button>
              </div>
            </template>

            <OrderList
              :orders="simulation.orders.pending"
              :selected-order="ui.selectedOrder"
              @select-order="selectOrder"
            />
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 添加订单对话框 -->
    <OrderCreateDialog
      v-model="showOrderDialog"
      :grid-size="simulation.grid.size"
      @create-order="createOrder"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useStore } from "vuex";
import { simulationAPI, presetConfigs, utils } from "@/api/simulation";
import SimulationCanvas from "@/components/SimulationCanvas.vue";
import VehicleList from "@/components/VehicleList.vue";
import OrderList from "@/components/OrderList.vue";
import OrderCreateDialog from "@/components/OrderCreateDialog.vue";

export default {
  name: "SimulationView",
  components: {
    SimulationCanvas,
    VehicleList,
    OrderList,
    OrderCreateDialog,
  },

  setup() {
    const store = useStore();

    // 响应式数据
    const selectedPreset = ref("medium");
    const creating = ref(false);
    const showOrderDialog = ref(false);
    const currentConfig = ref(presetConfigs.medium);

    // 计算属性
    const simulation = computed(() => store.state.simulation);
    const ui = computed(() => store.state.ui);
    const websocket = computed(() => store.state.websocket);

    const hasSimulation = computed(() => {
      return simulation.value.vehicles.length > 0;
    });

    const activeVehicleCount = computed(() => store.getters.activeVehicleCount);
    const pendingOrderCount = computed(() => store.getters.pendingOrderCount);

    // 方法
    const loadPreset = (presetName) => {
      if (presetConfigs[presetName]) {
        currentConfig.value = { ...presetConfigs[presetName] };
        console.log("📋 加载预设配置:", presetName, currentConfig.value);
      }
    };

    const createSimulation = async () => {
      creating.value = true;
      try {
        const result = await simulationAPI.createSimulation(
          currentConfig.value
        );
        utils.showSuccess("仿真创建成功");
        console.log("✅ 仿真创建成功:", result);

        // 获取初始状态
        await refreshState();
      } catch (error) {
        utils.showError(`仿真创建失败: ${utils.formatError(error)}`);
      } finally {
        creating.value = false;
      }
    };

    const startSimulation = async () => {
      try {
        await simulationAPI.startSimulation(true);
        utils.showSuccess("仿真已启动");
      } catch (error) {
        utils.showError(`启动失败: ${utils.formatError(error)}`);
      }
    };

    const stopSimulation = async () => {
      try {
        await simulationAPI.stopSimulation();
        utils.showSuccess("仿真已停止");
      } catch (error) {
        utils.showError(`停止失败: ${utils.formatError(error)}`);
      }
    };

    const stepSimulation = async () => {
      try {
        await simulationAPI.stepSimulation();
        // 状态会通过WebSocket自动更新
      } catch (error) {
        utils.showError(`单步执行失败: ${utils.formatError(error)}`);
      }
    };

    const resetSimulation = async () => {
      try {
        await simulationAPI.resetSimulation(currentConfig.value);
        utils.showSuccess("仿真已重置");
        await refreshState();
      } catch (error) {
        utils.showError(`重置失败: ${utils.formatError(error)}`);
      }
    };

    const refreshState = async () => {
      try {
        const state = await simulationAPI.getSimulationState();
        if (state.status === "success") {
          store.dispatch("updateSimulation", {
            isRunning: state.is_running,
            step: state.step,
            vehicles: state.vehicles || [],
            orders: state.orders || { pending: [], statistics: {} },
            grid: state.grid || {
              size: 15,
              obstacles: [],
              charging_stations: [],
            },
            statistics: state.statistics || {},
            config: state.config || {},
          });
        }
      } catch (error) {
        console.error("获取状态失败:", error);
      }
    };

    const createOrder = async (orderData) => {
      try {
        await simulationAPI.createOrder(orderData.pickup, orderData.delivery);
        utils.showSuccess("订单创建成功");
        showOrderDialog.value = false;
      } catch (error) {
        utils.showError(`订单创建失败: ${utils.formatError(error)}`);
      }
    };

    const selectVehicle = (vehicleId) => {
      store.dispatch("selectVehicle", vehicleId);
    };

    const selectOrder = (orderId) => {
      store.dispatch("selectOrder", orderId);
    };

    const toggleShowPath = () => {
      store.commit("TOGGLE_SHOW_PATH");
    };

    const toggleShowGrid = () => {
      store.commit("TOGGLE_SHOW_GRID");
    };

    const onGridClick = (position) => {
      console.log("网格点击:", position);
      // 可以在这里添加交互逻辑，如设置订单位置
    };

    // 生命周期
    onMounted(async () => {
      console.log("🖥️ 仿真视图加载完成");

      // 加载默认预设
      loadPreset(selectedPreset.value);

      // 尝试获取当前状态
      await refreshState();
    });

    return {
      // 响应式数据
      selectedPreset,
      creating,
      showOrderDialog,

      // 计算属性
      simulation,
      ui,
      websocket,
      hasSimulation,
      activeVehicleCount,
      pendingOrderCount,

      // 方法
      loadPreset,
      createSimulation,
      startSimulation,
      stopSimulation,
      stepSimulation,
      resetSimulation,
      createOrder,
      selectVehicle,
      selectOrder,
      toggleShowPath,
      toggleShowGrid,
      onGridClick,
    };
  },
};
</script>

<style lang="scss" scoped>
.simulation-view {
  padding: 24px 32px;
  height: calc(100vh - 60px);
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.control-panel {
  flex-shrink: 0;

  .control-card {
    background: linear-gradient(to bottom right, #ffffff, #f8f9fa);

    .control-content {
      .quick-config {
        .el-select {
          width: 100%;

          :deep(.el-input__wrapper) {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;

            &:hover {
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
          }
        }
      }

      .simulation-controls {
        text-align: center;

        .el-button-group {
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
          border-radius: 8px;
          overflow: hidden;
        }
      }

      .statistics {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        padding: 20px;
        border-radius: 8px;
        margin-top: 16px;

        .el-statistic {
          text-align: center;
          position: relative;

          &::before {
            content: "";
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 2px;
          }

          :deep(.el-statistic__head) {
            font-size: 14px;
            color: #909399;
            margin-bottom: 8px;
            font-weight: 500;
          }

          :deep(.el-statistic__content) {
            font-size: 32px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: pulse-number 2s ease-in-out infinite;
          }
        }
      }
    }
  }
}

@keyframes pulse-number {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.main-content {
  flex: 1;
  overflow: hidden;

  .visualization-card {
    height: calc(100vh - 200px);
    position: relative;
    overflow: hidden;

    &::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
      background-size: 200% 100%;
      animation: gradient-slide 3s ease infinite;
      z-index: 1;
    }

    .view-controls {
      display: flex;
      gap: 8px;

      .el-button {
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(102, 126, 234, 0.2);

        &.el-button--primary {
          background: rgba(102, 126, 234, 0.9);
          color: white;
        }
      }
    }

    :deep(.el-card__body) {
      height: calc(100% - 60px);
      padding: 0;
      background: #fafbfc;
    }
  }

  .info-card {
    height: calc((100vh - 200px) / 2 - 8px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
      .card-header .title {
        color: #667eea;
      }
    }

    :deep(.el-card__body) {
      height: calc(100% - 60px);
      overflow-y: auto;
      padding: 16px;

      // 自定义滚动条
      &::-webkit-scrollbar {
        width: 8px;
      }

      &::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
      }

      &::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 4px;

        &:hover {
          background: linear-gradient(180deg, #5568d3, #6a3f8f);
        }
      }
    }
  }
}

@keyframes gradient-slide {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .simulation-view {
    padding: 16px 20px;
  }

  .main-content {
    .el-col:last-child {
      margin-top: 16px;
    }
  }
}

@media (max-width: 768px) {
  .control-panel {
    .quick-config {
      .el-col {
        margin-bottom: 8px;
      }
    }
  }

  .main-content {
    .visualization-card {
      height: 400px;
    }

    .info-card {
      height: 300px;
    }
  }
}
</style>
