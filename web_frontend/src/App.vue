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
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 60px;
  line-height: 60px;
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

  .logo-icon {
    color: white;
  }

  .app-title {
    color: white;
    font-size: 24px;
    font-weight: bold;
    margin: 0;
  }
}

.header-menu {
  background: transparent;
  border-bottom: none;

  .el-menu-item {
    color: rgba(255, 255, 255, 0.8);
    border-bottom: 2px solid transparent;

    &:hover,
    &.is-active {
      background-color: rgba(255, 255, 255, 0.1);
      color: white;
      border-bottom-color: white;
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
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);

  .el-card__header {
    background-color: #fafafa;
    border-bottom: 1px solid #e4e7ed;
    padding: 16px 20px;

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .title {
        font-size: 16px;
        font-weight: bold;
        color: #303133;
        margin: 0;
      }
    }
  }
}

.el-button {
  border-radius: 6px;

  &.is-circle {
    border-radius: 50%;
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
