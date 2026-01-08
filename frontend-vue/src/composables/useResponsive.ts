import { onMounted } from 'vue'
export function useResponsive() {
  function adjust() {
    const w = window.innerWidth
    document.body.classList.remove('is-mobile','is-tablet','is-desktop')
    if (w <= 768) document.body.classList.add('is-mobile')
    else if (w <= 1024) document.body.classList.add('is-tablet')
    else document.body.classList.add('is-desktop')
  }
  onMounted(() => { adjust(); window.addEventListener('resize', adjust) })
}

