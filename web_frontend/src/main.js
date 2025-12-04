/**
 * CampusFleet AI Vue.js 前端入口
 */
import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import { createStore } from "vuex";
import ElementPlus from "element-plus";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import "element-plus/dist/index.css";

import App from "./App.vue";
import SimulationView from "./views/SimulationView.vue";
import MultiAgentDashboard from "./views/MultiAgentDashboard.vue";

// 路由配置
const routes = [
  {
    path: "/",
    name: "Simulation",
    component: SimulationView,
    meta: { title: "仿真控制台" },
  },
  {
    path: "/multi-agent",
    name: "MultiAgent",
    component: MultiAgentDashboard,
    meta: { title: "多智能体监控" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Vuex状态管理
const store = createStore({
  state: {
    // 仿真状态
    simulation: {
      isRunning: false,
      step: 0,
      vehicles: [],
      orders: {
        pending: [],
        statistics: {},
      },
      grid: {
        size: 15,
        obstacles: [],
        charging_stations: [],
      },
      statistics: {},
      config: {},
    },

    // WebSocket连接状态
    websocket: {
      connected: false,
      reconnecting: false,
      lastUpdate: null,
    },

    // UI状态
    ui: {
      selectedVehicle: null,
      selectedOrder: null,
      showPath: true,
      showGrid: true,
      autoStep: true,
    },
  },

  mutations: {
    // 更新仿真状态
    UPDATE_SIMULATION(state, data) {
      state.simulation = { ...state.simulation, ...data };
      state.websocket.lastUpdate = new Date();
    },

    // WebSocket状态
    SET_WEBSOCKET_CONNECTED(state, connected) {
      state.websocket.connected = connected;
    },

    SET_WEBSOCKET_RECONNECTING(state, reconnecting) {
      state.websocket.reconnecting = reconnecting;
    },

    // UI状态
    SET_SELECTED_VEHICLE(state, vehicleId) {
      state.ui.selectedVehicle = vehicleId;
    },

    SET_SELECTED_ORDER(state, orderId) {
      state.ui.selectedOrder = orderId;
    },

    TOGGLE_SHOW_PATH(state) {
      state.ui.showPath = !state.ui.showPath;
    },

    TOGGLE_SHOW_GRID(state) {
      state.ui.showGrid = !state.ui.showGrid;
    },

    SET_AUTO_STEP(state, autoStep) {
      state.ui.autoStep = autoStep;
    },
  },

  actions: {
    // 更新仿真数据
    updateSimulation({ commit }, data) {
      commit("UPDATE_SIMULATION", data);
    },

    // WebSocket操作
    setWebSocketConnected({ commit }, connected) {
      commit("SET_WEBSOCKET_CONNECTED", connected);
    },

    setWebSocketReconnecting({ commit }, reconnecting) {
      commit("SET_WEBSOCKET_RECONNECTING", reconnecting);
    },

    // 选择车辆
    selectVehicle({ commit }, vehicleId) {
      commit("SET_SELECTED_VEHICLE", vehicleId);
    },

    // 选择订单
    selectOrder({ commit }, orderId) {
      commit("SET_SELECTED_ORDER", orderId);
    },
  },

  getters: {
    // 获取选中的车辆详情
    selectedVehicleData: (state) => {
      if (!state.ui.selectedVehicle) return null;
      return state.simulation.vehicles.find(
        (v) => v.id === state.ui.selectedVehicle
      );
    },

    // 获取选中的订单详情
    selectedOrderData: (state) => {
      if (!state.ui.selectedOrder) return null;
      return state.simulation.orders.pending.find(
        (o) => o.id === state.ui.selectedOrder
      );
    },

    // 获取运行中的车辆数量
    activeVehicleCount: (state) => {
      return state.simulation.vehicles.filter((v) => v.state !== "Idle").length;
    },

    // 获取待处理订单数量
    pendingOrderCount: (state) => {
      return state.simulation.orders.pending.length;
    },
  },
});

// 创建Vue应用
const app = createApp(App);

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

// 使用插件
app.use(ElementPlus);
app.use(router);
app.use(store);

// 全局属性
app.config.globalProperties.$ELEMENT = { size: "default" };

// 挂载应用
app.mount("#app");

console.log("🌐 CampusFleet AI Frontend 启动成功");
console.log("🚀 特性: VRP拼单 + MAPF协调 + 实时可视化");
