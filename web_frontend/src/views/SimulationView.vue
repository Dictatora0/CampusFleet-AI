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
              <el-col :span="6">
                <el-select
                  v-model="selectedPreset"
                  placeholder="选择预设"
                  @change="loadPreset"
                >
                  <el-option label="🎯 贪心算法（启发式）" value="greedy" />
                  <el-option label="🎪 拍卖机制（多智能体）" value="auction" />
                  <el-option label="🤖 强化学习（深度学习）" value="rl" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-input-number
                  v-model="initialOrderCount"
                  :min="0"
                  :max="20"
                  placeholder="初始订单数"
                  style="width: 100%"
                >
                  <template #prefix>📦</template>
                </el-input-number>
              </el-col>
              <el-col :span="6">
                <el-button
                  type="primary"
                  @click="createSimulation"
                  :loading="creating"
                  style="width: 100%"
                >
                  <el-icon><Plus /></el-icon>
                  创建仿真
                </el-button>
              </el-col>
              <el-col :span="6">
                <el-button
                  type="danger"
                  @click="resetSimulation"
                  :disabled="!hasSimulation"
                  style="width: 100%"
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
        <!-- 可视化面板（包含Canvas和侧边信息） -->
        <el-col :span="24">
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

            <!-- 内部flex布局：左Canvas + 右信息面板 -->
            <div class="canvas-container">
              <div class="canvas-area">
                <SimulationCanvas
                  :grid-size="simulation.grid.size"
                  :vehicles="simulation.vehicles"
                  :orders="simulation.orders.pending"
                  :obstacles="simulation.grid.obstacles"
                  :charging-stations="simulation.grid.charging_stations"
                  @cell-click="onGridClick"
                />
              </div>

              <!-- 右侧信息面板 -->
              <div class="side-panels">
                <!-- 图例说明 -->
                <el-card class="info-card legend-card mb-16">
                  <template #header>
                    <div class="card-header">
                      <h3 class="title">
                        <el-icon><Document /></el-icon>
                        图例说明
                      </h3>
                    </div>
                  </template>

                  <div class="legend-items">
                    <div class="legend-item">
                      <div class="legend-icon obstacle-icon"></div>
                      <span>障碍物</span>
                    </div>
                    <div class="legend-item">
                      <div class="legend-icon charging-icon">⚡</div>
                      <span>充电站</span>
                    </div>
                    <div class="legend-item">
                      <div class="legend-icon vehicle-icon vehicle-good"></div>
                      <span>电量充足(≥50%)</span>
                    </div>
                    <div class="legend-item">
                      <div
                        class="legend-icon vehicle-icon vehicle-medium"
                      ></div>
                      <span>电量中等(30-50%)</span>
                    </div>
                    <div class="legend-item">
                      <div class="legend-icon vehicle-icon vehicle-low"></div>
                      <span>电量低(10-30%)</span>
                    </div>
                    <div class="legend-item">
                      <div
                        class="legend-icon vehicle-icon vehicle-critical"
                      ></div>
                      <span>严重低电(&lt;10%)</span>
                    </div>
                    <div class="legend-item">
                      <div class="legend-icon order-pickup"></div>
                      <span>取货点</span>
                    </div>
                    <div class="legend-item">
                      <div class="legend-icon order-delivery"></div>
                      <span>送货点</span>
                    </div>
                  </div>
                </el-card>

                <!-- 车辆信息 -->
                <el-card class="info-card mb-16">
                  <template #header>
                    <div class="card-header">
                      <h3 class="title">
                        <el-icon><Van /></el-icon>
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

                <!-- 拍卖日志面板 -->
                <el-card class="info-card auction-card">
                  <AuctionLogPanel :strategy="simulation.strategy" />
                </el-card>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 添加订单对话框 -->
    <OrderCreateDialog
      v-model="showOrderDialog"
      :grid-size="simulation.grid.size"
      @create="createOrder"
      @create-random="createRandomOrder"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useStore } from "vuex";
import { Operation, Van } from "@element-plus/icons-vue";
import { simulationAPI, presetConfigs, utils } from "@/api/simulation";
import SimulationCanvas from "@/components/SimulationCanvas.vue";
import VehicleList from "@/components/VehicleList.vue";
import OrderList from "@/components/OrderList.vue";
import OrderCreateDialog from "@/components/OrderCreateDialog.vue";
import AuctionLogPanel from "@/components/AuctionLogPanel.vue";

export default {
  name: "SimulationView",
  components: {
    SimulationCanvas,
    VehicleList,
    OrderList,
    OrderCreateDialog,
    AuctionLogPanel,
    Operation,
    Van,
  },

  setup() {
    const store = useStore();

    // 响应式数据
    const selectedPreset = ref("auction");
    const creating = ref(false);
    const showOrderDialog = ref(false);
    const currentConfig = ref(presetConfigs.auction);
    const initialOrderCount = ref(5); // 默认创建5个订单

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

        // 自动添加随机订单（如果设置了数量）
        if (initialOrderCount.value > 0) {
          console.log(`🎲 自动添加 ${initialOrderCount.value} 个初始订单...`);
          const orderPromises = [];
          for (let i = 0; i < initialOrderCount.value; i++) {
            orderPromises.push(simulationAPI.createRandomOrder());
          }
          await Promise.all(orderPromises);
          utils.showSuccess(`已自动添加${initialOrderCount.value}个随机订单`);
          console.log("✅ 初始订单添加完成");

          // 刷新状态以显示订单
          await refreshState();
        }
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
            strategy: state.strategy || "", // 添加策略字段
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

    const createRandomOrder = async () => {
      try {
        await simulationAPI.createRandomOrder();
        utils.showSuccess("随机订单创建成功");
        showOrderDialog.value = false;
      } catch (error) {
        utils.showError(`随机订单创建失败: ${utils.formatError(error)}`);
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
      initialOrderCount,

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
      createRandomOrder,
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
  min-height: calc(100vh - 60px);
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
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
  overflow: visible;

  .visualization-card {
    min-height: 1080px;
    position: relative;
    overflow: visible;

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
      padding: 16px;
      background: #fafbfc;
    }
  }

  // Canvas容器flex布局
  .canvas-container {
    display: flex;
    gap: 20px;
    align-items: flex-start;
    width: 100%;

    .canvas-area {
      flex-shrink: 0;
    }

    .side-panels {
      flex: 1; // 自动填充所有剩余空间
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-width: 280px;
      // 移除max-width，让它占满所有剩余空间
    }
  }

  .info-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
      transform: translateY(-2px);

      .card-header .title {
        color: #667eea;
      }
    }

    :deep(.el-card__body) {
      max-height: 320px;
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

// 图例卡片样式
.legend-card {
  .legend-items {
    display: grid;
    grid-template-columns: repeat(2, 1fr); // 2列网格布局
    gap: 12px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: #555;
    padding: 6px 10px;
    border-radius: 6px;
    transition: all 0.2s;

    &:hover {
      background: rgba(102, 126, 234, 0.05);
      transform: translateX(4px);
    }

    .legend-icon {
      width: 28px;
      height: 28px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;

      &.obstacle-icon {
        background: #424242;
      }

      &.charging-icon {
        background: #4caf50;
        color: white;
        font-size: 18px;
        border-radius: 50%;
      }

      &.vehicle-icon {
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);

        &.vehicle-good {
          background: #4caf50;
        }

        &.vehicle-medium {
          background: #ffc107;
        }

        &.vehicle-low {
          background: #ff5722;
        }

        &.vehicle-critical {
          background: #f44336;
        }
      }

      &.order-pickup {
        background: #4caf50;
      }

      &.order-delivery {
        background: #2196f3;
      }
    }

    span {
      flex: 1;
      font-weight: 500;
    }
  }
}

// 拍卖日志卡片样式
.auction-card {
  margin-top: 16px;

  :deep(.el-card__body) {
    padding: 0;
    height: 500px;
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
      min-height: 1080px;
    }
  }
}
</style>
