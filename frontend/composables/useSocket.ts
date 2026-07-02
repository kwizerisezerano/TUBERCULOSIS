import { io, Socket } from 'socket.io-client'

export function useSocket() {
  const socket = ref<Socket | null>(null)
  const isConnected = ref(false)
  const config = useRuntimeConfig()

  const connect = () => {
    if (socket.value) {
      return
    }

    const socketUrl = config.public.apiBase || 'http://127.0.0.1:5000'
    // Remove /api from the URL for WebSocket connection
    const wsUrl = socketUrl.replace('/api', '')
    socket.value = io(wsUrl, {
      transports: ['websocket', 'polling']
    })

    socket.value.on('connect', () => {
      isConnected.value = true
    })

    socket.value.on('connect_error', (error: any) => {
      console.error('WebSocket connection error:', error)
    })

    socket.value.on('disconnect', () => {
      isConnected.value = false
    })
  }

  const disconnect = () => {
    socket.value?.disconnect()
    socket.value = null
    isConnected.value = false
  }

  const subscribePatients = (params?: any) => {
    socket.value?.emit('subscribe_patients', params)
  }

  const onPatientsUpdate = (callback: (data: any) => void) => {
    socket.value?.on('patients_update', callback)
  }

  const offPatientsUpdate = (callback: (data: any) => void) => {
    socket.value?.off('patients_update', callback)
  }

  return {
    socket,
    isConnected,
    connect,
    disconnect,
    subscribePatients,
    onPatientsUpdate,
    offPatientsUpdate
  }
}