<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <el-header class="main-header">
      <div class="header-content">
        <div class="logo-section">
          <el-icon class="logo-icon" size="32">
            <TruckFilled />
          </el-icon>
          <h1 class="app-title">CampusFleet AI</h1>
          <el-tag type="success" size="small">v3.0</el-tag>
        </div>

        <!-- 导航菜单 -->
        <el-menu
          :default-active="$route.path"
          class="header-menu"
          mode="horizontal"
          router
        >
          <el-menu-item index="/">
            <el-icon><Monitor /></el-icon>
            仿真控制台
          </el-menu-item>
          <el-menu-item index="/multi-agent">
            <el-icon><Van /></el-icon>
            多智能体监控
          </el-menu-item>
          <el-menu-item index="/analytics">
            <el-icon><DataAnalysis /></el-icon>
            数据分析
          </el-menu-item>
          <el-menu-item index="/about">
            <el-icon><InfoFilled /></el-icon>
            关于系统
          </el-menu-item>
        </el-menu>

        <!-- 连接状态 -->
        <div class="status-section">
          <el-tooltip :content="websocketStatus" placement="bottom">
            <el-badge
              :is-dot="true"
              :type="websocket.connected ? 'success' : 'danger'"
              class="connection-badge"
            >
              <el-icon size="20">
                <Connection />
              </el-icon>
            </el-badge>
          </el-tooltip>
        </div>
      </div>
    </el-header>

    <!-- 主体内容区域 -->
    <el-container class="main-container">
      <router-view />
    </el-container>

    <!-- 全局加载遮罩 -->
    <el-loading
      v-loading="websocket.reconnecting"
      element-loading-text="正在重新连接..."
      element-loading-background="rgba(0, 0, 0, 0.7)"
    />
  </div>
</template>

<script>
import { computed } from "vue";
import { useStore } from "vuex";
import WebSocketManager from "@/utils/websocket";

export default {
  name: "App",
  setup() {
    const store = useStore();

    // WebSocket管理器
    const wsManager = new WebSocketManager();

    // 启动WebSocket连接
    wsManager.connect();

    // 计算属性
    const websocket = computed(() => store.state.websocket);

    const websocketStatus = computed(() => {
      if (websocket.value.connected) {
        return `已连接 - 最后更新: ${
          websocket.value.lastUpdate?.toLocaleTimeString() || "未知"
        }`;
      } else if (websocket.value.reconnecting) {
        return "正在重连...";
      } else {
        return "连接断开";
      }
    });

    return {
      websocket,
      websocketStatus,
    };
  },
};
</script>

<style lang="scss">
// 全局样式
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB",
    "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  background-color: #f5f7fa;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

// 顶部导航栏样式
.main-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: none;
  box-shadow: 0 4px 20px 0 rgba(102, 126, 234, 0.3);
  padding: 0;
  height: 60px;
  line-height: 60px;
  position: relative;
  overflow: hidden;

  // 添加动态背景效果
  &::before {
    content: "";
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(
      circle,
      rgba(255, 255, 255, 0.1) 0%,
      transparent 70%
    );
    animation: pulse 15s ease-in-out infinite;
  }
}

@keyframes pulse {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-10%, -10%) scale(1.1);
  }
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;

  .logo-icon {
    color: white;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
    animation: float 3s ease-in-out infinite;
  }

  .app-title {
    color: white;
    font-size: 24px;
    font-weight: bold;
    margin: 0;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    letter-spacing: 1px;
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.header-menu {
  background: transparent;
  border-bottom: none;
  position: relative;
  z-index: 1;

  .el-menu-item {
    color: rgba(255, 255, 255, 0.85);
    border-bottom: 2px solid transparent;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;

    &::after {
      content: "";
      position: absolute;
      bottom: 0;
      left: 50%;
      width: 0;
      height: 2px;
      background: white;
      transition: all 0.3s ease;
      transform: translateX(-50%);
    }

    &:hover {
      background-color: rgba(255, 255, 255, 0.15);
      color: white;
      transform: translateY(-2px);

      &::after {
        width: 80%;
      }
    }

    &.is-active {
      background-color: rgba(255, 255, 255, 0.2);
      color: white;
      font-weight: 600;

      &::after {
        width: 100%;
      }
    }
  }
}

.status-section {
  display: flex;
  align-items: center;
  gap: 16px;

  .connection-badge {
    .el-icon {
      color: white;
    }
  }
}

// 主容器样式
.main-container {
  flex: 1;
  background-color: #f5f7fa;
}

// Element Plus 自定义样式
.el-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    box-shadow: 0 8px 30px 0 rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
  }

  .el-card__header {
    background: linear-gradient(to right, #fafbfc 0%, #ffffff 100%);
    border-bottom: 2px solid #f0f0f0;
    padding: 18px 24px;

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .title {
        font-size: 17px;
        font-weight: 700;
        color: #303133;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;

        .el-icon {
          color: #667eea;
        }
      }
    }
  }
}

.el-button {
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  &:active {
    transform: translateY(0);
  }

  &.is-circle {
    border-radius: 50%;
  }

  &.el-button--primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;

    &:hover {
      background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
    }
  }

  &.el-button--success {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    border: none;
  }

  &.el-button--warning {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    border: none;
  }

  &.el-button--danger {
    background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    border: none;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .header-content {
    padding: 0 12px;
  }

  .logo-section .app-title {
    font-size: 20px;
  }

  .header-menu .el-menu-item {
    font-size: 14px;
    padding: 0 12px;
  }
}

// 动画效果
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 滑入动画
.slide-fade-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}

// 缩放动画
.scale-enter-active,
.scale-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

// 弹跳效果
@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.bounce {
  animation: bounce 1s ease infinite;
}

// 闪烁效果
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.shimmer {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite;
}

// 工具类
.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.mb-16 {
  margin-bottom: 16px;
}

.mb-24 {
  margin-bottom: 24px;
}

.flex {
  display: flex;
}

.flex-1 {
  flex: 1;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-12 {
  gap: 12px;
}

.gap-16 {
  gap: 16px;
}
</style>
