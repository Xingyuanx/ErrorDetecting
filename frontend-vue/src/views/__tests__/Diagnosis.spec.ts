import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Diagnosis from "../Diagnosis.vue";

const mocks = vi.hoisted(() => ({
  elMessageWarning: vi.fn(),
  elMessageError: vi.fn(),
  mockClusterList: vi.fn(),
  mockNodesByCluster: vi.fn(),
  mockGetHistory: vi.fn(),
  mockDiagnoseRepair: vi.fn(),
}));

vi.mock("element-plus", () => ({
  ElMessage: {
    warning: mocks.elMessageWarning,
    error: mocks.elMessageError,
  },
}));

vi.mock("../../api/cluster.service", () => ({
  ClusterService: { list: () => mocks.mockClusterList() },
}));

vi.mock("../../api/node.service", () => ({
  NodeService: { listByCluster: (uuid: string) => mocks.mockNodesByCluster(uuid) },
}));

vi.mock("../../api/diagnosis.service", () => ({
  DiagnosisService: {
    getHistory: (sid: string) => mocks.mockGetHistory(sid),
    diagnoseRepair: (p: any) => mocks.mockDiagnoseRepair(p),
  },
}));

vi.mock("../../stores/auth", () => ({
  useAuthStore: () => ({ token: "test-token" }),
}));

function flush() {
  return new Promise((r) => setTimeout(r, 0));
}

const stubs = {
  SplitPane: {
    template: "<div><slot name='first' /><slot name='second' /></div>",
  },
  LogViewer: {
    template: "<div></div>",
  },
  transition: { template: "<div><slot /></div>" },
  "el-icon": { template: "<i><slot /></i>" },
  "el-tag": { props: ["type", "size"], template: "<span><slot /></span>" },
  "el-scrollbar": { template: "<div><slot /></div>" },
  "el-card": {
    template:
      '<section class="el-card"><header class="el-card__header"><slot name="header"/></header><div class="el-card__body"><slot /></div></section>',
  },
  "el-select": {
    props: ["modelValue"],
    emits: ["update:modelValue"],
    template:
      '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target && $event.target.value)"><slot /></select>',
  },
  "el-option": { template: "<option></option>" },
  "el-input": {
    props: ["modelValue", "type", "rows", "disabled", "placeholder"],
    emits: ["update:modelValue"],
    template:
      '<textarea :value="modelValue" :disabled="disabled" @input="$emit(\'update:modelValue\', $event.target && $event.target.value)" />',
  },
  "el-button": {
    props: ["disabled", "type", "plain", "circle", "loading", "link"],
    emits: ["click"],
    template:
      '<button v-bind="$attrs" :disabled="disabled" @click="$emit(\'click\')"><slot /></button>',
  },
  "el-checkbox": {
    props: ["modelValue", "label", "disabled"],
    emits: ["update:modelValue"],
    template:
      '<label><input type="checkbox" :checked="modelValue" :disabled="disabled" @change="$emit(\'update:modelValue\', $event.target && $event.target.checked)" /><span><slot /></span></label>',
  },
  "el-collapse": { template: "<div><slot /></div>" },
  "el-collapse-item": { template: "<div><slot /></div>" },
};

describe("Diagnosis关键链路", () => {
  beforeEach(() => {
    mocks.elMessageWarning.mockReset();
    mocks.elMessageError.mockReset();
    mocks.mockClusterList.mockReset();
    mocks.mockNodesByCluster.mockReset();
    mocks.mockGetHistory.mockReset();
    mocks.mockDiagnoseRepair.mockReset();
  });

  it("页面能打开、选择节点会拉取历史", async () => {
    mocks.mockClusterList.mockResolvedValue([
      { uuid: "c1", host: "cluster-1", count: 1 },
    ]);
    mocks.mockNodesByCluster.mockResolvedValue([{ name: "node-1", status: "running" }]);
    mocks.mockGetHistory
      .mockResolvedValueOnce({
        messages: [{ role: "assistant", content: "global-history" }],
      })
      .mockResolvedValueOnce({
        messages: [{ role: "assistant", content: "node-history" }],
      });

    const wrapper = mount(Diagnosis, {
      global: { stubs },
      attachTo: document.body,
    });

    await flush();
    await flush();

    expect(mocks.mockGetHistory).toHaveBeenCalledWith("diagnosis-global");

    const groupHeader = wrapper.find(".group-header");
    expect(groupHeader.exists()).toBe(true);
    await groupHeader.trigger("click");
    await flush();

    const nodeItem = wrapper.find(".node-item-v");
    expect(nodeItem.exists()).toBe(true);
    await nodeItem.trigger("click");
    await flush();

    expect(mocks.mockGetHistory).toHaveBeenCalledWith("diagnosis-node-1");
  });

  it("发送消息、停止、深度诊断按钮校验、滚动到底部提示", async () => {
    mocks.mockClusterList.mockResolvedValue([{ uuid: "c1", host: "cluster-1", count: 1 }]);
    mocks.mockNodesByCluster.mockResolvedValue([{ name: "node-1", status: "running" }]);
    mocks.mockGetHistory.mockResolvedValue({ messages: [{ role: "assistant", content: "history" }] });
    mocks.mockDiagnoseRepair.mockResolvedValue({ summary: "ok" });

    const wrapper = mount(Diagnosis, {
      global: { stubs },
      attachTo: document.body,
    });

    await flush();
    await flush();

    await wrapper.find(".group-header").trigger("click");
    await flush();
    await wrapper.find(".node-item-v").trigger("click");
    await flush();

    mocks.elMessageWarning.mockReset();
    const deepBtn = wrapper.findAll("button").find((b) => b.text().includes("深度诊断"));
    expect(deepBtn).toBeTruthy();

    const wrapperNoNode = mount(Diagnosis, { global: { stubs } });
    await flush();
    const deepBtn2 = wrapperNoNode.findAll("button").find((b) => b.text().includes("深度诊断"));
    expect(deepBtn2).toBeTruthy();
    await deepBtn2!.trigger("click");
    expect(mocks.elMessageWarning).toHaveBeenCalled();

    const originalFetch = globalThis.fetch;
    globalThis.fetch = vi.fn((_: any, init: any) => {
      return new Promise((_resolve, reject) => {
        const signal = init?.signal as AbortSignal | undefined;
        if (!signal) return reject({ name: "AbortError" });
        const onAbort = () => reject({ name: "AbortError" });
        if (signal.aborted) return reject({ name: "AbortError" });
        signal.addEventListener("abort", onAbort, { once: true });
      }) as any;
    }) as any;

    const textarea = wrapper.find("textarea");
    await textarea.setValue("hello");
    const sendBtn = wrapper.findAll("button").find((b) => b.text().trim() === "发送");
    expect(sendBtn).toBeTruthy();
    await sendBtn!.trigger("click");
    await flush();

    const stopBtn = wrapper.findAll("button").find((b) => b.text().includes("停止"));
    expect(stopBtn).toBeTruthy();
    await stopBtn!.trigger("click");
    await flush();

    globalThis.fetch = originalFetch as any;

    globalThis.fetch = vi.fn(async () => {
      const text = [
        'data: {"content":"hi"}\n',
        'data: {"content":"!"}\n',
        "data: [DONE]\n",
      ].join("");
      let used = false;
      return {
        ok: true,
        body: {
          getReader() {
            return {
              read: async () => {
                if (used) return { done: true, value: undefined };
                used = true;
                return { done: false, value: new TextEncoder().encode(text) };
              },
            };
          },
        },
      } as any;
    }) as any;

    await textarea.setValue("ping");
    const sendBtnAgain = wrapper.findAll("button").find((b) => b.text().trim() === "发送");
    expect(sendBtnAgain).toBeTruthy();
    await sendBtnAgain!.trigger("click");
    await flush();
    await flush();

    expect(wrapper.text()).toContain("hi");
    expect(wrapper.text()).toContain("!");

    globalThis.fetch = originalFetch as any;

    const historyEl = wrapper.find(".chat-history").element as HTMLElement;
    const scrollToSpy = vi.fn();
    (historyEl as any).scrollTo = scrollToSpy;
    Object.defineProperty(historyEl, "scrollHeight", { value: 1000, configurable: true });
    Object.defineProperty(historyEl, "clientHeight", { value: 100, configurable: true });
    Object.defineProperty(historyEl, "scrollTop", { value: 0, configurable: true });
    historyEl.dispatchEvent(new Event("scroll"));
    await flush();

    const scrollBottomBtn = wrapper.findAll("button").find((b) => b.element.classList.contains("scroll-bottom-btn"));
    expect(scrollBottomBtn).toBeTruthy();
    await scrollBottomBtn!.trigger("click");
    await flush();
    await flush();
    expect(scrollToSpy).toHaveBeenCalledWith({ top: 1000, behavior: "smooth" });
  });
});
