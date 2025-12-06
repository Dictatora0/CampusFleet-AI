<template>
  <div class="auction-log-panel">
    <div class="panel-header">
      <h3 class="title">
        <el-icon><TrendCharts /></el-icon>
        拍卖日志
      </h3>
      <el-tag :type="isAuctionStrategy ? 'success' : 'info'" size="small">
        {{ isAuctionStrategy ? "拍卖模式" : "非拍卖模式" }}
      </el-tag>
    </div>

    <div v-if="!isAuctionStrategy" class="no-auction-notice">
      <el-empty description="当前未使用拍卖策略" :image-size="80">
        <el-text class="hint-text">
          请在创建仿真时选择"拍卖机制(CNP)"策略
        </el-text>
      </el-empty>
    </div>

    <div v-else class="auction-content">
      <!-- 统计信息 -->
      <div class="auction-stats" v-if="latestAuction">
        <div class="stat-item">
          <div class="stat-value">{{ latestAuction.total_auctions }}</div>
          <div class="stat-label">总拍卖</div>
        </div>
        <div class="stat-item">
          <div class="stat-value success">
            {{ latestAuction.successful_auctions }}
          </div>
          <div class="stat-label">成功</div>
        </div>
        <div class="stat-item">
          <div class="stat-value warning">
            {{
              latestAuction.total_auctions - latestAuction.successful_auctions
            }}
          </div>
          <div class="stat-label">流拍</div>
        </div>
      </div>

      <!-- 拍卖日志时间线 -->
      <div class="auction-timeline">
        <el-scrollbar max-height="400px">
          <el-timeline v-if="auctionLogs.length > 0">
            <el-timeline-item
              v-for="(log, index) in auctionLogs"
              :key="index"
              :timestamp="formatPhase(log.phase)"
              :type="getLogType(log.phase)"
              :icon="getLogIcon(log.phase)"
              :size="log.phase === 'winner_selection' ? 'large' : 'normal'"
            >
              <div class="log-content">
                <!-- Announcement Phase -->
                <div
                  v-if="log.phase === 'announcement'"
                  class="log-announcement"
                >
                  <el-tag type="info" size="small"
                    >订单 #{{ log.order_id }}</el-tag
                  >
                  <span class="log-text">
                    发布拍卖 {{ log.pickup }} → {{ log.delivery }}
                  </span>
                  <el-tag type="" size="small"
                    >{{ log.bidders_count }} 个竞标者</el-tag
                  >
                </div>

                <!-- Winner Selection Phase -->
                <div v-if="log.phase === 'winner_selection'" class="log-winner">
                  <div class="winner-info">
                    <el-icon class="trophy-icon"><Trophy /></el-icon>
                    <span class="winner-text"
                      >车辆 #{{ log.winner_car_id }} 中标</span
                    >
                  </div>
                  <div class="bid-details">
                    <el-tag type="success" size="small">
                      中标成本: {{ log.winner_cost.toFixed(2) }}
                    </el-tag>
                    <el-tag v-if="log.runner_up_cost" type="info" size="small">
                      第二名: {{ log.runner_up_cost.toFixed(2) }}
                    </el-tag>
                    <el-tag type="" size="small">
                      共 {{ log.total_bids }} 个竞标
                    </el-tag>
                  </div>
                </div>

                <!-- Award Phase -->
                <div v-if="log.phase === 'award'" class="log-award">
                  <el-tag type="success" size="small">✓</el-tag>
                  <span class="log-text">
                    订单 #{{ log.order_id }} 已授予车辆 #{{ log.car_id }}
                  </span>
                </div>

                <!-- No Bids Phase -->
                <div v-if="log.phase === 'no_bids'" class="log-no-bids">
                  <el-tag type="danger" size="small">✗</el-tag>
                  <span class="log-text"> 订单 #{{ log.order_id }} 流拍 </span>
                  <el-tag type="warning" size="small">{{ log.reason }}</el-tag>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>

          <el-empty v-else description="暂无拍卖日志" :image-size="60" />
        </el-scrollbar>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { TrendCharts, Trophy } from "@element-plus/icons-vue";
import axios from "axios";

export default {
  name: "AuctionLogPanel",
  components: {
    TrendCharts,
    Trophy,
  },
  props: {
    strategy: {
      type: String,
      default: "",
    },
  },
  setup(props) {
    const auctionHistory = ref([]);
    const auctionLogs = ref([]);
    const latestAuction = ref(null);
    const refreshInterval = ref(null);

    const isAuctionStrategy = computed(() => {
      return props.strategy === "AUCTION_CNP";
    });

    const fetchAuctionLogs = async () => {
      if (!isAuctionStrategy.value) {
        return;
      }

      try {
        const response = await axios.get(
          "http://localhost:8001/api/auction/logs"
        );
        if (
          response.data.status === "success" &&
          response.data.auction_history.length > 0
        ) {
          auctionHistory.value = response.data.auction_history;

          // 获取最新的拍卖记录
          latestAuction.value =
            auctionHistory.value[auctionHistory.value.length - 1];

          // 展开所有日志（最新的在前）
          auctionLogs.value = latestAuction.value.logs || [];
        }
      } catch (error) {
        console.error("获取拍卖日志失败:", error);
      }
    };

    const formatPhase = (phase) => {
      const phaseMap = {
        announcement: "📢 发布",
        winner_selection: "🏆 中标",
        award: "✅ 授予",
        no_bids: "❌ 流拍",
      };
      return phaseMap[phase] || phase;
    };

    const getLogType = (phase) => {
      const typeMap = {
        announcement: "primary",
        winner_selection: "success",
        award: "success",
        no_bids: "danger",
      };
      return typeMap[phase] || "";
    };

    const getLogIcon = (phase) => {
      const iconMap = {
        announcement: "Bell",
        winner_selection: "Trophy",
        award: "Check",
        no_bids: "Close",
      };
      return iconMap[phase] || "InfoFilled";
    };

    // 监听策略变化
    watch(
      () => props.strategy,
      (newStrategy) => {
        if (newStrategy === "AUCTION_CNP") {
          fetchAuctionLogs();
          startAutoRefresh();
        } else {
          stopAutoRefresh();
          auctionLogs.value = [];
          latestAuction.value = null;
        }
      }
    );

    const startAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value);
      }
      refreshInterval.value = setInterval(fetchAuctionLogs, 2000); // 每2秒刷新
    };

    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value);
        refreshInterval.value = null;
      }
    };

    onMounted(() => {
      if (isAuctionStrategy.value) {
        fetchAuctionLogs();
        startAutoRefresh();
      }
    });

    onUnmounted(() => {
      stopAutoRefresh();
    });

    return {
      auctionHistory,
      auctionLogs,
      latestAuction,
      isAuctionStrategy,
      formatPhase,
      getLogType,
      getLogIcon,
    };
  },
};
</script>

<style scoped lang="scss">
.auction-log-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #eee;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

    .title {
      margin: 0;
      font-size: 14px;
      font-weight: 600;
      color: white;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .no-auction-notice {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;

    .hint-text {
      color: #909399;
      font-size: 12px;
    }
  }

  .auction-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .auction-stats {
    display: flex;
    justify-content: space-around;
    padding: 12px;
    background: #f5f7fa;
    border-bottom: 1px solid #eee;

    .stat-item {
      text-align: center;

      .stat-value {
        font-size: 20px;
        font-weight: bold;
        color: #303133;

        &.success {
          color: #67c23a;
        }

        &.warning {
          color: #e6a23c;
        }
      }

      .stat-label {
        font-size: 12px;
        color: #909399;
        margin-top: 4px;
      }
    }
  }

  .auction-timeline {
    flex: 1;
    padding: 16px;
    overflow: hidden;

    :deep(.el-timeline) {
      padding-left: 0;
    }

    .log-content {
      padding: 8px 0;
    }

    .log-announcement,
    .log-award,
    .log-no-bids {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;

      .log-text {
        font-size: 13px;
        color: #606266;
      }
    }

    .log-winner {
      .winner-info {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .trophy-icon {
          color: #f59e0b;
          font-size: 18px;
        }

        .winner-text {
          font-size: 14px;
          font-weight: 600;
          color: #303133;
        }
      }

      .bid-details {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
    }
  }
}
</style>
