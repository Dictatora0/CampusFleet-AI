/**
 * WebSocket管理器 - 处理实时数据通信
 */
import { ElNotification } from "element-plus";

let store = null;

// 动态导入store（避免循环依赖）
const getStore = async () => {
  if (!store) {
    const { createApp } = await import("vue");
    const app = createApp({});
    store = app.config.globalProperties.$store;

    // 如果还是获取不到，直接从window获取（开发环境）
    if (!store && window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
      store = window.__VUE_DEVTOOLS_GLOBAL_HOOK__.store;
    }
  }
  return store;
};

class WebSocketManager {
  constructor() {
    this.ws = null;
    this.reconnectTimer = null;
    this.heartbeatTimer = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
    this.heartbeatInterval = 30000;
    this.url = `ws://${location.host}/ws/simulation`;

    // 如果是开发环境，使用固定端口
    if (process.env.NODE_ENV === "development") {
      this.url = "ws://localhost:8000/ws/simulation";
    }
  }

  /**
   * 建立WebSocket连接
   */
  connect() {
    try {
      console.log(`🔗 正在连接WebSocket: ${this.url}`);

      this.ws = new WebSocket(this.url);

      this.ws.onopen = this.onOpen.bind(this);
      this.ws.onmessage = this.onMessage.bind(this);
      this.ws.onclose = this.onClose.bind(this);
      this.ws.onerror = this.onError.bind(this);
    } catch (error) {
      console.error("❌ WebSocket连接失败:", error);
      this.scheduleReconnect();
    }
  }

  /**
   * 连接成功
   */
  async onOpen(event) {
    console.log("✅ WebSocket连接成功");

    this.reconnectAttempts = 0;

    // 更新store状态
    const store = await getStore();
    if (store) {
      store.dispatch("setWebSocketConnected", true);
      store.dispatch("setWebSocketReconnecting", false);
    }

    // 启动心跳
    this.startHeartbeat();

    // 显示连接成功通知
    ElNotification({
      title: "连接成功",
      message: "WebSocket连接已建立",
      type: "success",
      duration: 2000,
    });
  }

  /**
   * 接收消息
   */
  async onMessage(event) {
    try {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case "initial_state":
        case "state_update":
          await this.handleStateUpdate(message.data);
          break;

        case "pong":
          console.log("💓 心跳响应");
          break;

        default:
          console.log("📨 未知消息类型:", message.type);
      }
    } catch (error) {
      console.error("❌ 消息解析失败:", error);
    }
  }

  /**
   * 处理状态更新
   */
  async handleStateUpdate(data) {
    const store = await getStore();
    if (store) {
      // 更新仿真状态
      if (data.status === "success") {
        store.dispatch("updateSimulation", {
          isRunning: data.is_running,
          step: data.step,
          vehicles: data.vehicles || [],
          orders: data.orders || { pending: [], statistics: {} },
          grid: data.grid || { size: 15, obstacles: [], charging_stations: [] },
          statistics: data.statistics || {},
          config: data.config || {},
        });
      }
    }
  }

  /**
   * 连接关闭
   */
  async onClose(event) {
    console.log("🔌 WebSocket连接关闭:", event.code, event.reason);

    const store = await getStore();
    if (store) {
      store.dispatch("setWebSocketConnected", false);
    }

    // 停止心跳
    this.stopHeartbeat();

    // 如果不是正常关闭，尝试重连
    if (event.code !== 1000) {
      this.scheduleReconnect();
    }
  }

  /**
   * 连接错误
   */
  async onError(error) {
    console.error("❌ WebSocket错误:", error);

    const store = await getStore();
    if (store) {
      store.dispatch("setWebSocketConnected", false);
    }
  }

  /**
   * 发送消息
   */
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      return true;
    } else {
      console.warn("⚠️ WebSocket未连接，消息发送失败");
      return false;
    }
  }

  /**
   * 启动心跳
   */
  startHeartbeat() {
    this.stopHeartbeat();

    this.heartbeatTimer = setInterval(() => {
      this.send({ type: "ping" });
    }, this.heartbeatInterval);
  }

  /**
   * 停止心跳
   */
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  /**
   * 安排重连
   */
  async scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(
        `❌ 重连失败，已达到最大尝试次数 (${this.maxReconnectAttempts})`
      );

      ElNotification({
        title: "连接失败",
        message: `WebSocket重连失败，请检查网络连接`,
        type: "error",
        duration: 5000,
      });

      const store = await getStore();
      if (store) {
        store.dispatch("setWebSocketReconnecting", false);
      }

      return;
    }

    const store = await getStore();
    if (store) {
      store.dispatch("setWebSocketReconnecting", true);
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectInterval * this.reconnectAttempts,
      30000
    );

    console.log(
      `🔄 计划在 ${delay}ms 后重连 (第${this.reconnectAttempts}次尝试)`
    );

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * 手动重连
   */
  async reconnect() {
    console.log("🔄 手动重连WebSocket");

    this.disconnect();
    this.reconnectAttempts = 0;

    const store = await getStore();
    if (store) {
      store.dispatch("setWebSocketReconnecting", true);
    }

    setTimeout(() => {
      this.connect();
    }, 1000);
  }

  /**
   * 断开连接
   */
  disconnect() {
    console.log("🔌 断开WebSocket连接");

    // 清理定时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    this.stopHeartbeat();

    // 关闭连接
    if (this.ws) {
      this.ws.close(1000, "手动断开");
      this.ws = null;
    }
  }

  /**
   * 获取连接状态
   */
  getConnectionState() {
    if (!this.ws) return "CLOSED";

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return "CONNECTING";
      case WebSocket.OPEN:
        return "OPEN";
      case WebSocket.CLOSING:
        return "CLOSING";
      case WebSocket.CLOSED:
        return "CLOSED";
      default:
        return "UNKNOWN";
    }
  }
}

export default WebSocketManager;
