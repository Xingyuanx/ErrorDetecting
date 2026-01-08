import { ref, watch } from "vue";

export function useCollapsiblePercent(options: {
  initialPercent: number;
  defaultExpandedPercent: number;
  minRememberPercent?: number;
}) {
  const minRememberPercent = options.minRememberPercent ?? 0;
  const percent = ref(options.initialPercent);
  const lastPercent = ref(options.initialPercent);
  const collapsed = ref(options.initialPercent <= 0);

  function toggle() {
    if (collapsed.value) {
      percent.value =
        lastPercent.value > minRememberPercent
          ? lastPercent.value
          : options.defaultExpandedPercent;
      collapsed.value = false;
    } else {
      lastPercent.value = percent.value;
      percent.value = 0;
      collapsed.value = true;
    }
  }

  watch(percent, (v) => {
    if (v > 0) {
      collapsed.value = false;
      lastPercent.value = v;
    } else {
      collapsed.value = true;
    }
  });

  return { percent, lastPercent, collapsed, toggle };
}

