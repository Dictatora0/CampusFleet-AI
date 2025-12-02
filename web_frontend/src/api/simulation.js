/**
 * 仿真控制API - RESTful接口调用
 */
import axios from "axios";
import { ElMessage, ElNotification } from "element-plus";

// 创建axios实例
const api = axios.create({
  baseURL:
    process.env.NODE_ENV === "development"
      ? "http://localhost:8000/api"
      : "/api",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log(`🌐 API请求: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error("❌ API请求错误:", error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API响应: ${response.config.url}`, response.data);
    return response.data;
  },
  (error) => {
    console.error("❌ API响应错误:", error);

    const message =
      error.response?.data?.detail || error.message || "网络请求失败";

    ElNotification({
      title: "API错误",
      message: message,
      type: "error",
      duration: 3000,
    });

    return Promise.reject(error);
  }
);

/**
 * 仿真控制API
 */
export const simulationAPI = {
  /**
   * 创建新仿真
   * @param {Object} config - 仿真配置
   * @returns {Promise}
   */
  createSimulation(config) {
    return api.post("/simulation/create", config);
  },

  /**
   * 获取仿真状态
   * @returns {Promise}
   */
  getSimulationState() {
    return api.get("/simulation/state");
  },

  /**
   * 控制仿真
   * @param {string} command - 控制命令
   * @param {Object} params - 参数
   * @returns {Promise}
   */
  controlSimulation(command, params = null) {
    return api.post("/simulation/control", {
      command,
      params,
    });
  },

  /**
   * 启动仿真
   * @param {boolean} autoStep - 是否自动步进
   * @returns {Promise}
   */
  startSimulation(autoStep = true) {
    return this.controlSimulation("start", { auto_step: autoStep });
  },

  /**
   * 停止仿真
   * @returns {Promise}
   */
  stopSimulation() {
    return this.controlSimulation("stop");
  },

  /**
   * 单步执行
   * @returns {Promise}
   */
  stepSimulation() {
    return this.controlSimulation("step");
  },

  /**
   * 重置仿真
   * @param {Object} config - 新配置
   * @returns {Promise}
   */
  resetSimulation(config) {
    return this.controlSimulation("reset", config);
  },

  /**
   * 创建订单
   * @param {Array} pickup - 取货点 [x, y]
   * @param {Array} delivery - 配送点 [x, y]
   * @returns {Promise}
   */
  createOrder(pickup, delivery) {
    return api.post("/orders/create", {
      pickup,
      delivery,
    });
  },

  /**
   * 获取可用策略
   * @returns {Promise}
   */
  getStrategies() {
    return api.get("/strategies");
  },

  /**
   * 导出分析数据
   * @returns {Promise}
   */
  exportAnalytics() {
    return api.get("/analytics/export");
  },
};

/**
 * 预设配置
 */
export const presetConfigs = {
  /**
   * 小规模测试
   */
  small: {
    grid_size: 8,
    num_cars: 2,
    strategy: "GREEDY_NEAREST",
    enable_logging: true,
    auto_step_interval: 1.0,
  },

  /**
   * 中等规模演示
   */
  medium: {
    grid_size: 12,
    num_cars: 4,
    strategy: "VRP_BATCHING",
    enable_logging: true,
    auto_step_interval: 0.8,
  },

  /**
   * 大规模仿真
   */
  large: {
    grid_size: 15,
    num_cars: 6,
    strategy: "MAPF_CBS",
    enable_logging: true,
    auto_step_interval: 0.5,
  },

  /**
   * MAPF协调演示
   */
  mapfDemo: {
    grid_size: 10,
    num_cars: 3,
    strategy: "MAPF_CBS",
    enable_logging: true,
    auto_step_interval: 1.5,
  },

  /**
   * VRP拼单演示
   */
  vrpDemo: {
    grid_size: 12,
    num_cars: 2,
    strategy: "VRP_BATCHING",
    enable_logging: true,
    auto_step_interval: 1.2,
  },
};

/**
 * 工具函数
 */
export const utils = {
  /**
   * 格式化错误消息
   * @param {Error} error - 错误对象
   * @returns {string}
   */
  formatError(error) {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    return error.message || "未知错误";
  },

  /**
   * 显示成功消息
   * @param {string} message - 消息内容
   */
  showSuccess(message) {
    ElMessage({
      type: "success",
      message,
      duration: 2000,
    });
  },

  /**
   * 显示错误消息
   * @param {string} message - 消息内容
   */
  showError(message) {
    ElMessage({
      type: "error",
      message,
      duration: 3000,
    });
  },

  /**
   * 显示警告消息
   * @param {string} message - 消息内容
   */
  showWarning(message) {
    ElMessage({
      type: "warning",
      message,
      duration: 2500,
    });
  },

  /**
   * 验证坐标
   * @param {Array} coordinate - 坐标 [x, y]
   * @param {number} gridSize - 网格大小
   * @returns {boolean}
   */
  validateCoordinate(coordinate, gridSize) {
    if (!Array.isArray(coordinate) || coordinate.length !== 2) {
      return false;
    }

    const [x, y] = coordinate;
    return (
      Number.isInteger(x) &&
      Number.isInteger(y) &&
      x >= 0 &&
      x < gridSize &&
      y >= 0 &&
      y < gridSize
    );
  },

  /**
   * 生成随机坐标
   * @param {number} gridSize - 网格大小
   * @returns {Array}
   */
  randomCoordinate(gridSize) {
    return [
      Math.floor(Math.random() * gridSize),
      Math.floor(Math.random() * gridSize),
    ];
  },

  /**
   * 计算距离
   * @param {Array} pos1 - 位置1 [x, y]
   * @param {Array} pos2 - 位置2 [x, y]
   * @returns {number}
   */
  calculateDistance(pos1, pos2) {
    return Math.abs(pos1[0] - pos2[0]) + Math.abs(pos1[1] - pos2[1]);
  },
};

export default api;
