import type { EChartsType } from "echarts/core";

type EchartsModule = {
  init: (dom: HTMLElement, theme?: unknown, opts?: unknown) => EChartsType;
  use: (plugins: unknown[]) => void;
};

let modulePromise: Promise<EchartsModule> | null = null;

export async function loadEcharts(): Promise<EchartsModule> {
  if (modulePromise) return modulePromise;
  modulePromise = (async () => {
    const echarts = (await import("echarts/core")) as unknown as EchartsModule;
    const { PieChart, LineChart } = await import("echarts/charts");
    const {
      TooltipComponent,
      LegendComponent,
      GridComponent,
      DatasetComponent,
    } = await import("echarts/components");
    const { CanvasRenderer } = await import("echarts/renderers");

    echarts.use([
      PieChart,
      LineChart,
      TooltipComponent,
      LegendComponent,
      GridComponent,
      DatasetComponent,
      CanvasRenderer,
    ]);

    return echarts;
  })();
  return modulePromise;
}

