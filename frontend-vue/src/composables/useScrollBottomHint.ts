import { nextTick, onBeforeUnmount, ref, watch } from "vue";

export function useScrollBottomHint(options?: { threshold?: number }) {
  const threshold = options?.threshold ?? 200;
  const el = ref<HTMLElement | null>(null);
  const showScrollBottom = ref(false);

  function handleScroll() {
    if (!el.value) return;
    const { scrollTop, scrollHeight, clientHeight } = el.value;
    showScrollBottom.value = scrollHeight - scrollTop - clientHeight > threshold;
  }

  function setEl(v: Element | null) {
    el.value = (v as HTMLElement | null) || null;
  }

  function scrollToBottom(smooth = true) {
    nextTick(() => {
      if (!el.value) return;
      el.value.scrollTo({
        top: el.value.scrollHeight,
        behavior: smooth ? "smooth" : "auto",
      });
    });
  }

  watch(el, (next, prev) => {
    if (prev) prev.removeEventListener("scroll", handleScroll);
    if (next) next.addEventListener("scroll", handleScroll);
  });

  onBeforeUnmount(() => {
    if (el.value) el.value.removeEventListener("scroll", handleScroll);
  });

  return { el, setEl, showScrollBottom, scrollToBottom };
}

