import { onBeforeUnmount, onMounted, ref } from "vue";

export function useIsMobile(breakpoint = 1024) {
  const isMobile = ref(window.innerWidth <= breakpoint);

  function update() {
    isMobile.value = window.innerWidth <= breakpoint;
  }

  onMounted(() => {
    window.addEventListener("resize", update);
  });

  onBeforeUnmount(() => {
    window.removeEventListener("resize", update);
  });

  return { isMobile, update };
}

