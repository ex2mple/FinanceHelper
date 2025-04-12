<template>
  <div class="chat-container">
    <Card class="chat-card">
      <template #title>
        <div class="flex items-center">
          <i class="pi pi-comments mr-2 text-xl"></i>
          <span>AI Помощник</span>
        </div>
      </template>
      <template #subtitle>
        <span class="text-sm">Задайте вопрос и получите ответ от нашего ИИ-советника</span>
      </template>
      <template #content>
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-chat">
            <i class="pi pi-comment text-4xl mb-3 opacity-50"></i>
            <p>Начните новую беседу с помощником</p>
          </div>
          <div v-else class="messages">
            <div v-for="(message, index) in messages" :key="index" 
                 :class="['message-bubble', message.isUser ? 'user-message' : 'ai-message']">
              <div class="message-avatar">
                <Avatar v-if="message.isUser" icon="pi pi-user" size="small" shape="circle" />
                <Avatar v-else icon="pi pi-android" class="ai-avatar" size="small" shape="circle" />
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="font-bold">{{ message.isUser ? 'Вы' : 'AI Помощник' }}</span>
                  <small class="message-time">{{ formatTime(message.timestamp) }}</small>
                </div>
                <div class="message-text" v-if="!message.isLoading">
                  <p v-html="formatMessageText(message.text)"></p>
                </div>
                <div v-else class="ai-typing">
                  <i class="pi pi-spin pi-spinner mr-2"></i>
                  <span>Генерация ответа...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <div class="chat-input-container">
          <div class="input-wrapper">
            <Textarea 
              v-model="userInput" 
              placeholder="Введите сообщение..." 
              autoResize 
              rows="1"
              class="chat-input"
              :disabled="isLoading"
              @keydown.enter.prevent="sendMessage"
            />
            <Button 
              icon="pi pi-send" 
              class="send-button p-button-rounded" 
              :disabled="!userInput.trim() || isLoading"
              @click="sendMessage"
              aria-label="Отправить"
            />
          </div>
          <small v-if="error" class="error-message" style="color: red;">{{ error }}</small>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import axiosInstance from '~/axiosInstance'

interface Message {
  text: string
  isUser: boolean
  timestamp: Date
  isLoading?: boolean
}

const userInput = ref('')
const messages = ref<Message[]>([])
const isLoading = ref(false)
const error = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

const formatTime = (date: Date) => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatMessageText = (text: string) => {
  // Convert line breaks to <br> tags
  return text.replace(/\n/g, '<br>')
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return
  
  // Add user message
  const userMessage = {
    text: userInput.value,
    isUser: true,
    timestamp: new Date()
  }
  messages.value.push(userMessage)
  
  // Add loading message from AI
  const loadingMessage: Message = {
    text: '',
    isUser: false,
    timestamp: new Date(),
    isLoading: true
  }
  messages.value.push(loadingMessage)
  
  // Clear input and scroll to bottom
  userInput.value = ''
  await scrollToBottom()
  
  // Set loading state
  isLoading.value = true
  error.value = ''
  
  try {
    // Make API request to the /ai/ask/large endpoint
    const response = await axiosInstance.post('/ai/ask/large', {
      content: userMessage.text  // Changed from 'message' to 'content'
    })
    
    // Replace loading message with actual response
    const loadingIndex = messages.value.findIndex(m => m.isLoading)
    if (loadingIndex !== -1) {
      messages.value[loadingIndex] = {
        text: response.data,
        isUser: false,
        timestamp: new Date()
      }
    }
  } catch (err: any) {
    // Handle error
    error.value = err.response?.data?.message || 'Не удалось получить ответ от помощника'
    
    // Remove loading message
    messages.value = messages.value.filter(m => !m.isLoading)
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

// Scroll to bottom whenever messages are updated
watch(messages, () => {
  scrollToBottom()
})

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-container {
  padding: 1rem;
  max-width: 1000px;
  margin: 0 auto;
  height: calc(100vh - 150px);
  display: flex;
  flex-direction: column;
}

.chat-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.chat-card :deep(.p-card-body) {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.chat-card :deep(.p-card-content) {
  flex: 1;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  scroll-behavior: smooth;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-bubble {
  display: flex;
  gap: 0.75rem;
  max-width: 85%;
  animation: fadeIn 0.3s ease-in-out;
}

.message-avatar {
  flex-shrink: 0;
  align-self: flex-start;
  margin-top: 4px;
}

.ai-avatar :deep(.p-avatar) {
  background-color: var(--primary-color);
  color: white;
}

.message-content {
  flex: 1;
  background-color: var(--surface-200);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  overflow-wrap: break-word;
}

.user-message {
  align-self: flex-end;
}

.user-message .message-content {
  background-color: var(--primary-color);
  color: var(--primary-color-text);
}

.user-message .message-avatar {
  order: 2;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.message-time {
  opacity: 0.7;
  font-size: 0.75rem;
}

.message-text {
  line-height: 1.5;
}

.chat-input-container {
  padding: 1rem;
  background-color: var(--surface-card);
  border-top: 1px solid var(--surface-border);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
}

.chat-input {
  flex: 1;
  border-radius: 1.5rem;
  resize: none;
  max-height: 120px;
}

.send-button {
  align-self: flex-end;
}

.ai-typing {
  display: flex;
  align-items: center;
  opacity: 0.7;
  font-style: italic;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-color-secondary);
  text-align: center;
  padding: 2rem;
}

.error-message {
  color: var(--red-500);
  margin-top: 0.5rem;
  display: block;
}

/* Animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive styles */
@media (max-width: 768px) {
  .chat-container {
    padding: 0.5rem;
    height: calc(100vh - 120px);
  }
  
  .message-bubble {
    max-width: 95%;
  }
}
</style>