import api from '../lib/api'
import type { LogEntry } from '../types'

export const DiagnosisService = {
  /** AI 聊天接口 (支持流式) */
  async chat(payload: {
    sessionId: string;
    message: string;
    stream?: boolean;
    context?: {
      model?: string;
      agent?: string;
      [key: string]: any;
    };
  }): Promise<any> {
    return api.post('/v1/ai/chat', payload)
  },

  /** 故障诊断与自动修复接口 */
  async diagnoseRepair(payload: {
    cluster: string;
    model: string;
    auto?: boolean;
    maxSteps?: number;
  }): Promise<any> {
    return api.post('/v1/ai/diagnose-repair', payload)
  },

  /** 获取对话历史 */
  async getHistory(sessionId: string): Promise<any> {
    return api.get('/v1/ai/history', { params: { sessionId } })
  },

  /** 获取日志流 (保留原有功能) */
  async getLogs(clusterId: string, nodeId: string): Promise<{ logs: LogEntry[] }> {
    return api.get(`/v1/diagnosis/logs`, {
      params: { cluster_id: clusterId, node_id: nodeId }
    })
  }
}
