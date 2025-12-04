<template>
  <div class="multi-agent-dashboard">
    <h1 class="dashboard-title">🤖 多智能体系统监控面板</h1>

    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon vehicle-icon">🚗</div>
          <div class="stat-content">
            <div class="stat-value">{{ vehicleCount }}</div>
            <div class="stat-label">车辆智能体</div>
            <div class="stat-sub">活跃: {{ activeVehicles }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon order-icon">📦</div>
          <div class="stat-content">
            <div class="stat-value">{{ orderCount }}</div>
            <div class="stat-label">订单智能体</div>
            <div class="stat-sub">待处理: {{ pendingOrders }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon comm-icon">📡</div>
          <div class="stat-content">
            <div class="stat-value">{{ communicationCount }}</div>
            <div class="stat-label">通信消息</div>
            <div class="stat-sub">本轮: {{ currentStepMessages }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon perf-icon">📊</div>
          <div class="stat-content">
            <div class="stat-value">{{ completionRate }}%</div>
            <div class="stat-label">完成率</div>
            <div class="stat-sub">等级: {{ performanceGrade }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧：智能体状态面板 -->
      <el-col :span="8">
        <el-card class="panel-card agent-status-panel">
          <template #header>
            <div class="card-header">
              <span>🤖 智能体状态面板</span>
              <el-button type="primary" size="small" @click="refreshAgentStatus"
                >刷新</el-button
              >
            </div>
          </template>

          <el-tabs v-model="activeAgentTab">
            <!-- 车辆智能体 -->
            <el-tab-pane label="车辆智能体" name="vehicles">
              <div class="agent-list">
                <div
                  v-for="vehicle in agents.vehicles"
                  :key="vehicle.id"
                  class="agent-item vehicle-item"
                >
                  <div class="agent-header">
                    <span class="agent-id">🚗 车辆 #{{ vehicle.id }}</span>
                    <el-tag
                      :type="vehicle.status === 'idle' ? 'info' : 'success'"
                      size="small"
                    >
                      {{ vehicle.status === "idle" ? "空闲" : "忙碌" }}
                    </el-tag>
                  </div>
                  <div class="agent-details">
                    <div class="detail-item">
                      <span class="label">位置:</span>
                      <span class="value"
                        >({{ vehicle.position[0] }},
                        {{ vehicle.position[1] }})</span
                      >
                    </div>
                    <div class="detail-item">
                      <span class="label">感知:</span>
                      <span class="value"
                        >范围 {{ vehicle.perception.range }} 格</span
                      >
                    </div>
                    <div class="detail-item">
                      <span class="label">决策:</span>
                      <span class="value">{{ vehicle.decision.method }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">行动:</span>
                      <span class="value">{{ vehicle.action.current }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">已完成:</span>
                      <span class="value"
                        >{{ vehicle.completed_orders }} 个订单</span
                      >
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- 调度智能体 -->
            <el-tab-pane label="调度智能体" name="scheduler">
              <div class="agent-item scheduler-item">
                <div class="agent-header">
                  <span class="agent-id">🤖 调度智能体</span>
                </div>
                <div class="agent-details">
                  <div class="detail-item">
                    <span class="label">策略:</span>
                    <span class="value">{{ agents.scheduler.strategy }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">总分配:</span>
                    <span class="value"
                      >{{ agents.scheduler.total_assignments }} 次</span
                    >
                  </div>
                  <div class="detail-item">
                    <span class="label">活跃车辆:</span>
                    <span class="value"
                      >{{ agents.scheduler.active_vehicles }} 辆</span
                    >
                  </div>
                  <div class="detail-item">
                    <span class="label">待分配订单:</span>
                    <span class="value"
                      >{{ agents.scheduler.pending_orders }} 个</span
                    >
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- 环境智能体 -->
            <el-tab-pane label="环境智能体" name="environment">
              <div class="agent-item environment-item">
                <div class="agent-header">
                  <span class="agent-id">🌍 环境智能体</span>
                </div>
                <div class="agent-details">
                  <div class="detail-item">
                    <span class="label">网格大小:</span>
                    <span class="value"
                      >{{ agents.environment.grid_size }}×{{
                        agents.environment.grid_size
                      }}</span
                    >
                  </div>
                  <div class="detail-item">
                    <span class="label">当前步骤:</span>
                    <span class="value">{{
                      agents.environment.current_step
                    }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">总订单数:</span>
                    <span class="value">{{
                      agents.environment.total_orders
                    }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">已完成:</span>
                    <span class="value">{{
                      agents.environment.completed_orders
                    }}</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 中间：通信日志窗口 -->
      <el-col :span="8">
        <el-card class="panel-card communication-panel">
          <template #header>
            <div class="card-header">
              <span>📡 通信日志窗口</span>
              <el-button
                type="primary"
                size="small"
                @click="refreshCommunication"
                >刷新</el-button
              >
            </div>
          </template>

          <div class="comm-stats">
            <el-statistic
              title="状态报告"
              :value="communicationStats.status_reports"
              suffix="条"
            />
            <el-statistic
              title="任务分配"
              :value="communicationStats.task_assignments"
              suffix="条"
            />
          </div>

          <div class="communication-log">
            <div
              v-for="(log, index) in communicationLogs"
              :key="index"
              :class="['log-item', `log-${log.type}`]"
            >
              <div class="log-header">
                <el-tag :type="getLogTypeColor(log.type)" size="small">{{
                  getLogTypeName(log.type)
                }}</el-tag>
                <span class="log-time">步骤 {{ log.step }}</span>
              </div>
              <div class="log-body">
                <span class="log-sender">{{ log.sender }}</span>
                <span class="log-arrow">→</span>
                <span class="log-receiver">{{ log.receiver }}</span>
              </div>
              <div class="log-message">{{ log.message }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：协作决策可视化 -->
      <el-col :span="8">
        <el-card class="panel-card collaboration-panel">
          <template #header>
            <div class="card-header">
              <span>🤝 协作决策可视化</span>
              <el-button
                type="primary"
                size="small"
                @click="refreshCollaboration"
                >刷新</el-button
              >
            </div>
          </template>

          <div class="collab-metrics">
            <div class="metric-item">
              <div class="metric-label">车辆利用率</div>
              <el-progress
                :percentage="
                  Math.round(collaborationMetrics.vehicle_utilization * 100)
                "
                :color="
                  getProgressColor(collaborationMetrics.vehicle_utilization)
                "
              />
            </div>
            <div class="metric-item">
              <div class="metric-label">并行执行</div>
              <div class="metric-value">
                {{ collaborationMetrics.parallel_execution }} 辆车
              </div>
            </div>
          </div>

          <div class="assignments-list">
            <h4>当前任务分配</h4>
            <div
              v-for="assignment in assignments"
              :key="`${assignment.vehicle_id}-${assignment.order_id}`"
              class="assignment-item"
            >
              <div class="assignment-header">
                <span class="assignment-vehicle"
                  >🚗 车辆 #{{ assignment.vehicle_id }}</span
                >
                <span class="assignment-arrow">→</span>
                <span class="assignment-order"
                  >📦 订单 #{{ assignment.order_id }}</span
                >
              </div>
              <div class="assignment-details">
                <span class="detail"
                  >距离: {{ assignment.distance_to_pickup }} 格</span
                >
                <span class="detail">ETA: {{ assignment.eta_steps }} 步</span>
              </div>
              <div class="assignment-reason">
                <el-tag size="small" type="info">{{
                  assignment.decision_reason
                }}</el-tag>
              </div>
            </div>
            <div v-if="assignments.length === 0" class="no-assignments">
              当前无活跃任务分配
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部：实时性能图表 -->
    <el-row :gutter="20" class="bottom-content">
      <el-col :span="24">
        <el-card class="panel-card performance-panel">
          <template #header>
            <div class="card-header">
              <span>📊 实时性能图表</span>
              <el-button type="primary" size="small" @click="refreshPerformance"
                >刷新</el-button
              >
            </div>
          </template>

          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic
                title="完成率"
                :value="performanceMetrics.completion_rate"
                suffix="%"
              />
            </el-col>
            <el-col :span="6">
              <el-statistic
                title="已完成订单"
                :value="performanceMetrics.completed_orders"
              />
            </el-col>
            <el-col :span="6">
              <el-statistic
                title="待处理订单"
                :value="performanceMetrics.pending_orders"
              />
            </el-col>
            <el-col :span="6">
              <el-statistic
                title="车辆利用率"
                :value="performanceMetrics.vehicle_utilization"
                suffix="%"
              />
            </el-col>
          </el-row>

          <div class="performance-grade">
            <h3>
              系统性能等级:
              <el-tag :type="getGradeColor(performanceGrade)" size="large">{{
                performanceGrade
              }}</el-tag>
            </h3>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from "vue";
import axios from "axios";

export default {
  name: "MultiAgentDashboard",
  setup() {
    const API_BASE = "http://localhost:8001/api";

    // 数据状态
    const agents = reactive({
      vehicles: [],
      orders: [],
      scheduler: {},
      environment: {},
    });

    const communicationLogs = ref([]);
    const communicationStats = reactive({
      status_reports: 0,
      task_assignments: 0,
    });

    const assignments = ref([]);
    const collaborationMetrics = reactive({
      vehicle_utilization: 0,
      parallel_execution: 0,
    });

    const performanceMetrics = reactive({
      completion_rate: 0,
      completed_orders: 0,
      total_orders: 0,
      pending_orders: 0,
      vehicle_utilization: 0,
    });

    const vehicleCount = ref(0);
    const orderCount = ref(0);
    const activeVehicles = ref(0);
    const pendingOrders = ref(0);
    const communicationCount = ref(0);
    const currentStepMessages = ref(0);
    const completionRate = ref(0);
    const performanceGrade = ref("C");

    const activeAgentTab = ref("vehicles");

    let refreshInterval = null;

    // 刷新智能体状态
    const refreshAgentStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE}/agents/status`);
        if (response.data.status === "success") {
          agents.vehicles = response.data.agents.vehicles;
          agents.orders = response.data.agents.orders;
          agents.scheduler = response.data.agents.scheduler;
          agents.environment = response.data.agents.environment;

          vehicleCount.value = agents.vehicles.length;
          orderCount.value = agents.orders.length;
          activeVehicles.value = agents.scheduler.active_vehicles || 0;
          pendingOrders.value = agents.scheduler.pending_orders || 0;
        }
      } catch (error) {
        console.error("获取智能体状态失败:", error);
      }
    };

    // 刷新通信日志
    const refreshCommunication = async () => {
      try {
        const response = await axios.get(`${API_BASE}/communication/logs`);
        if (response.data.status === "success") {
          communicationLogs.value = response.data.logs;
          Object.assign(communicationStats, response.data.communication_stats);
          communicationCount.value = response.data.total_messages;
          currentStepMessages.value = response.data.logs.length;
        }
      } catch (error) {
        console.error("获取通信日志失败:", error);
      }
    };

    // 刷新协作决策
    const refreshCollaboration = async () => {
      try {
        const response = await axios.get(`${API_BASE}/collaboration/decisions`);
        if (response.data.status === "success") {
          assignments.value = response.data.assignments;
          Object.assign(
            collaborationMetrics,
            response.data.collaboration_metrics
          );
        }
      } catch (error) {
        console.error("获取协作决策失败:", error);
      }
    };

    // 刷新性能指标
    const refreshPerformance = async () => {
      try {
        const response = await axios.get(`${API_BASE}/performance/metrics`);
        if (response.data.status === "success") {
          Object.assign(performanceMetrics, response.data.metrics);
          completionRate.value = response.data.metrics.completion_rate;
          performanceGrade.value = response.data.performance_grade;
        }
      } catch (error) {
        console.error("获取性能指标失败:", error);
      }
    };

    // 刷新所有数据
    const refreshAll = () => {
      refreshAgentStatus();
      refreshCommunication();
      refreshCollaboration();
      refreshPerformance();
    };

    // 工具函数
    const getLogTypeColor = (type) => {
      const colors = {
        status_report: "info",
        task_assignment: "success",
        completion_notification: "warning",
      };
      return colors[type] || "info";
    };

    const getLogTypeName = (type) => {
      const names = {
        status_report: "状态报告",
        task_assignment: "任务分配",
        completion_notification: "完成通知",
      };
      return names[type] || type;
    };

    const getProgressColor = (value) => {
      if (value > 0.7) return "#67c23a";
      if (value > 0.4) return "#e6a23c";
      return "#f56c6c";
    };

    const getGradeColor = (grade) => {
      const colors = {
        A: "success",
        B: "warning",
        C: "danger",
      };
      return colors[grade] || "info";
    };

    // 生命周期
    onMounted(() => {
      refreshAll();
      // 每2秒自动刷新
      refreshInterval = setInterval(refreshAll, 2000);
    });

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    });

    return {
      agents,
      communicationLogs,
      communicationStats,
      assignments,
      collaborationMetrics,
      performanceMetrics,
      vehicleCount,
      orderCount,
      activeVehicles,
      pendingOrders,
      communicationCount,
      currentStepMessages,
      completionRate,
      performanceGrade,
      activeAgentTab,
      refreshAgentStatus,
      refreshCommunication,
      refreshCollaboration,
      refreshPerformance,
      getLogTypeColor,
      getLogTypeName,
      getProgressColor,
      getGradeColor,
    };
  },
};
</script>

<style scoped>
.multi-agent-dashboard {
  padding: 24px 32px;
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
  width: 100%;
}

.dashboard-title {
  text-align: center;
  margin-bottom: 30px;
  font-size: 28px;
  color: #303133;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 15px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 48px;
  margin-right: 15px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin: 5px 0;
}

.stat-sub {
  font-size: 12px;
  color: #606266;
}

.main-content,
.bottom-content {
  margin-bottom: 20px;
}

.panel-card {
  height: 600px;
  overflow: hidden;
}

.performance-panel {
  height: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.agent-list {
  max-height: 480px;
  overflow-y: auto;
}

.agent-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.agent-id {
  font-size: 16px;
}

.agent-details {
  font-size: 13px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item .label {
  color: #909399;
  font-weight: 500;
}

.detail-item .value {
  color: #303133;
  font-weight: 600;
}

.comm-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.communication-log {
  max-height: 450px;
  overflow-y: auto;
}

.log-item {
  background: white;
  border-left: 3px solid #409eff;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
}

.log-item.log-status_report {
  border-left-color: #909399;
}

.log-item.log-task_assignment {
  border-left-color: #67c23a;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.log-time {
  font-size: 12px;
  color: #909399;
}

.log-body {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
  font-weight: 500;
}

.log-sender,
.log-receiver {
  color: #409eff;
}

.log-arrow {
  color: #909399;
}

.log-message {
  font-size: 13px;
  color: #606266;
}

.collab-metrics {
  margin-bottom: 20px;
}

.metric-item {
  margin-bottom: 20px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.assignments-list {
  max-height: 400px;
  overflow-y: auto;
}

.assignments-list h4 {
  margin-bottom: 15px;
  color: #303133;
}

.assignment-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.assignment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
}

.assignment-arrow {
  color: #909399;
}

.assignment-details {
  display: flex;
  gap: 15px;
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.no-assignments {
  text-align: center;
  padding: 40px;
  color: #909399;
  font-style: italic;
}

.performance-grade {
  margin-top: 20px;
  text-align: center;
}

.performance-grade h3 {
  color: #303133;
}
</style>
