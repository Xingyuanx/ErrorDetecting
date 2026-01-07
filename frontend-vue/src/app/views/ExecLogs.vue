<template>
  <div class="exec-logs-container">
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">集群操作日志</h2>
        <p class="page-subtitle">查看与管理修复执行记录，支持完整后端同步</p>
      </div>
      <div class="header-actions"></div>
    </div>

    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>执行记录</span>
        </div>
      </template>
      <ExecLogsTable
        :records="displayRecords"
        :selected-id="selected"
        @select="select"
        @delete="del"
      />
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :layout="
            isMobile
              ? 'prev, pager, next'
              : 'total, sizes, prev, pager, next, jumper'
          "
          :pager-count="isMobile ? 5 : 7"
          :small="isMobile"
          :total="records.length"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted, onUnmounted } from "vue";
import { LogService } from "../api/log.service";
import { useAuthStore } from "../stores/auth";
import ExecLogsTable from "../components/ExecLogsTable.vue";
import { ElMessage } from "element-plus";

type RecordItem = {
  id: number;
  clusterName: string;
  username: string;
  description: string;
  faultId: string;
  cmdType: string;
  status: "running" | "success" | "failed";
  start: string;
  end: string | "";
  code: number | null;
};

const isMobile = ref(window.innerWidth < 768);
const updateWidth = () => {
  isMobile.value = window.innerWidth < 768;
};

const auth = useAuthStore();
const records = reactive<RecordItem[]>([]);
const selected = ref<number | null>(null);
const loading = ref(false);

// 分页相关状态
const currentPage = ref(1);
const pageSize = ref(20);

// 计算当前页显示的记录
const displayRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return records.slice(start, end);
});

function handleSizeChange(val: number) {
  pageSize.value = val;
  currentPage.value = 1;
}

function handleCurrentChange(val: number) {
  currentPage.value = val;
}

function select(r: RecordItem) {
  selected.value = r.id;
}

async function del(id: number) {
  try {
    await LogService.removeExecLog(id);
    const i = records.findIndex((x) => x.id === id);
    if (i >= 0) {
      records.splice(i, 1);
      if (selected.value === id) selected.value = null;
    }
    ElMessage.success("删除成功");
  } catch (e: any) {
    ElMessage.error(
      "删除失败：" + (e.friendlyMessage || e.message || "网络错误")
    );
  }
}

async function load() {
  loading.value = true;
  try {
    const items = await LogService.listExecLogs();
    const normalized: RecordItem[] = items.map((d: any) => ({
      id: d.id,
      clusterName: d.cluster_name || "",
      username: d.username || d.user_name || d.user?.username || "",
      description: d.description || "",
      faultId: d.fault_id || "",
      cmdType: d.command_type || "",
      status: d.execution_status || "running",
      start: (d.start_time || "").replace("T", " ").slice(0, 19),
      end: d.end_time ? String(d.end_time).replace("T", " ").slice(0, 19) : "",
      code: d.exit_code ?? null,
    }));
    records.splice(0, records.length, ...normalized);
  } catch (e: any) {
    ElMessage.error(
      "加载集群操作日志失败：" + (e.friendlyMessage || e.message || "网络错误")
    );
    records.splice(0, records.length);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  load();
  window.addEventListener("resize", updateWidth);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateWidth);
});
</script>

<style scoped>
.exec-logs-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.page-subtitle {
  color: #6b7280;
  font-size: 14px;
  margin: 4px 0 0 0;
}

.table-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.card-header {
  font-weight: 600;
}

.w-full {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .pagination-wrapper {
    justify-content: center;
  }
}
</style>
