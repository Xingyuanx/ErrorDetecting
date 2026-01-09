import { computed, reactive, ref, type Ref } from "vue";
import { ClusterService } from "../api/cluster.service";
import { NodeService } from "../api/node.service";

type NodeItem = { name: string; status: string };
export type ClusterGroup = {
  id: string;
  uuid: string;
  name: string;
  open: boolean;
  nodes: NodeItem[];
  count?: number;
};

export function useClusterTree(options: {
  kw: Ref<string>;
  filters: { cluster: string; node: string };
  selectedNode: Ref<string>;
  setError: (e: any, def: string) => void;
}) {
  const groups = reactive<ClusterGroup[]>([]);
  const loadingSidebar = ref(false);

  function pad3(n: number) {
    return String(n).padStart(3, "0");
  }

  async function loadClusters() {
    loadingSidebar.value = true;
    try {
      const list = await ClusterService.list();
      const mapped: ClusterGroup[] = list
        .map((x: any) => ({
          id: String(x.uuid || x.id || x.host || x.name || ""),
          uuid: String(x.uuid || x.id || ""),
          name: String(x.host || x.name || x.uuid || ""),
          open: false,
          nodes: [],
          count: Number(x.count) || 0,
        }))
        .filter((g: any) => g.id && g.name);
      groups.splice(0, groups.length, ...mapped);
    } catch (e: any) {
      options.setError(e, "集群列表加载失败");
    } finally {
      loadingSidebar.value = false;
    }
  }

  async function loadNodesFor(clusterUuid: string) {
    const g = groups.find((x) => x.uuid === clusterUuid);
    if (!g) return;
    const clusterName = g.name;
    try {
      const nodes = await NodeService.listByCluster(clusterUuid);
      const mappedNodes = nodes
        .map((x: any) => ({
          name: String(x?.name || x),
          status: x?.status || "running",
        }))
        .filter((x: any) => x.name);
      if (mappedNodes.length) g.nodes = mappedNodes;
      else if ((g.count || 0) > 0)
        g.nodes = Array.from({ length: g.count as number }, (_, i) => ({
          name: `${clusterName}-${pad3(i + 1)}`,
          status: "running",
        }));
    } catch (e: any) {
      if ((g.count || 0) > 0 && g.nodes.length === 0)
        g.nodes = Array.from({ length: g.count as number }, (_, i) => ({
          name: `${clusterName}-${pad3(i + 1)}`,
          status: "running",
        }));
      options.setError(e, "节点列表加载失败");
    }
  }

  async function toggleGroup(g: ClusterGroup) {
    g.open = !g.open;
    if (g.open && g.nodes.length === 0) await loadNodesFor(g.uuid);
  }

  const filteredGroups = computed(() => {
    const kraw = options.kw.value.trim().toLowerCase();
    let base = groups.filter((g) => !options.filters.cluster || g.name === options.filters.cluster);
    if (kraw) {
      base = base.filter(
        (g) =>
          g.name.toLowerCase().includes(kraw) ||
          g.nodes.some((n) => n.name.toLowerCase().includes(kraw))
      );
    }
    if (options.filters.node) {
      base = base.filter((g) => g.nodes.some((n) => n.name === options.filters.node));
    }
    return base;
  });

  function nodesForGroup(g: ClusterGroup) {
    const k = options.kw.value.trim().toLowerCase();
    let nodes = g.nodes;
    if (k) nodes = nodes.filter((n) => n.name.toLowerCase().includes(k) || g.name.toLowerCase().includes(k));
    if (options.filters.node) nodes = nodes.filter((n) => n.name === options.filters.node);
    return nodes;
  }

  function statusDot(n: { name: string; status: string }) {
    if (n.status === "running") return "status-dot-running";
    if (n.status === "warning") return "status-dot-warning";
    if (n.status === "error") return "status-dot-error";
    return n.name.includes("003")
      ? "status-dot-error"
      : n.name.includes("002")
      ? "status-dot-warning"
      : "status-dot-running";
  }

  const selectedClusterUuid = computed(() => {
    if (!options.selectedNode.value) return "";
    const group = groups.find((g) => g.nodes.some((n) => n.name === options.selectedNode.value));
    return group ? group.uuid : "";
  });

  return {
    groups,
    loadingSidebar,
    filteredGroups,
    nodesForGroup,
    toggleGroup,
    statusDot,
    selectedClusterUuid,
    loadClusters,
  };
}

