<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建订单"
    width="500px"
    @close="handleClose"
  >
    <el-form :model="orderForm" label-width="100px">
      <el-form-item label="取货点">
        <el-row :gutter="10">
          <el-col :span="12">
            <el-input-number
              v-model="orderForm.pickup.x"
              :min="0"
              :max="gridSize - 1"
              placeholder="X坐标"
            />
          </el-col>
          <el-col :span="12">
            <el-input-number
              v-model="orderForm.pickup.y"
              :min="0"
              :max="gridSize - 1"
              placeholder="Y坐标"
            />
          </el-col>
        </el-row>
      </el-form-item>

      <el-form-item label="送货点">
        <el-row :gutter="10">
          <el-col :span="12">
            <el-input-number
              v-model="orderForm.delivery.x"
              :min="0"
              :max="gridSize - 1"
              placeholder="X坐标"
            />
          </el-col>
          <el-col :span="12">
            <el-input-number
              v-model="orderForm.delivery.y"
              :min="0"
              :max="gridSize - 1"
              placeholder="Y坐标"
            />
          </el-col>
        </el-row>
      </el-form-item>

      <el-form-item label="优先级">
        <el-rate v-model="orderForm.priority" :max="3" />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit">创建</el-button>
        <el-button type="success" @click="handleRandomOrder"
          >随机订单</el-button
        >
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { ref, watch } from "vue";

export default {
  name: "OrderCreateDialog",
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    gridSize: {
      type: Number,
      default: 15,
    },
  },
  emits: ["update:visible", "create", "create-random"],
  setup(props, { emit }) {
    const dialogVisible = ref(props.visible);
    const orderForm = ref({
      pickup: { x: 0, y: 0 },
      delivery: { x: 5, y: 5 },
      priority: 1,
    });

    watch(
      () => props.visible,
      (newVal) => {
        dialogVisible.value = newVal;
      }
    );

    watch(dialogVisible, (newVal) => {
      emit("update:visible", newVal);
    });

    const handleClose = () => {
      dialogVisible.value = false;
    };

    const handleSubmit = () => {
      const order = {
        pickup: [orderForm.value.pickup.x, orderForm.value.pickup.y],
        delivery: [orderForm.value.delivery.x, orderForm.value.delivery.y],
        priority: orderForm.value.priority,
      };
      emit("create", order);
      handleClose();
    };

    const handleRandomOrder = () => {
      emit("create-random");
      handleClose();
    };

    return {
      dialogVisible,
      orderForm,
      handleClose,
      handleSubmit,
      handleRandomOrder,
    };
  },
};
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
