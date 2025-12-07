import * as echarts from 'echarts'
export function initCpu(el: HTMLElement) {
  const c = echarts.init(el)
  c.setOption({ xAxis: { type: 'category', boundaryGap: false, data: ['00:00','04:00','08:00','12:00','16:00','20:00','24:00'] }, yAxis: { type: 'value', min:0, max:100 }, series: [{ type: 'line', smooth: true, data: [20,35,45,60,55,40,30] }] })
  return c
}
export function initMem(el: HTMLElement) {
  const c = echarts.init(el)
  c.setOption({ series: [{ type: 'pie', radius: ['40%','70%'], data: [{ value: 8.5, name: '已使用' }, { value: 15.5, name: '可用' }] }] })
  return c
}

