<template>
  <div class="sop-dashboard h-full flex flex-col min-h-0" >
    <div class="flex justify-between items-center mb-6 shrink-0">
      <div>
        <h1>SOPs & Documents</h1>
        <p class="text-sm text-muted">
          Library of standard operating procedures with global AI Assistant.
        </p>
      </div>
      <button class="btn btn-primary" @click="showUploadModal = true">
        + Upload SOP (PDF)
      </button>
    </div>

    <div class="main-grid flex flex-1 gap-6 overflow-hidden pb-4 min-h-0">
      <!-- LEFT: DOCUMENT LIBRARY -->
      <div class="w-1/2 flex flex-col gap-4 min-h-0">
        <div v-if="!selectedDoc" class="card flex-1 overflow-hidden p-0 library-card">
          <div class="library-header p-3 border-b border-color bg-surface sticky top-0 z-10">
            <h2 class="library-title">Document Library</h2>
            <input
              type="text"
              v-model="searchQuery"
              class="form-control library-search m-0"
              placeholder="Search SOPs..."
            />
          </div>

          <div class="p-3 flex flex-col gap-3 overflow-y-auto">
            <div v-if="isLoadingDocs" class="text-center text-muted py-4 text-sm">
              Loading documents...
            </div>

            <div v-else-if="filteredDocs.length === 0" class="text-center text-muted py-4 text-sm">
              No SOPs found.
            </div>

            <div
              v-else
              v-for="doc in filteredDocs"
              :key="doc.id"
              class="doc-item"
              @click="selectDocument(doc)"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div class="doc-icon-wrap">
                  <svg
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    width="18"
                    height="18"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                    ></path>
                  </svg>
                </div>

                <div class="min-w-0">
                  <h3 class="doc-title">{{ doc.title }}</h3>
                  <p class="doc-meta">{{ doc.category }} • {{ formatDate(doc.created_at) }}</p>
                </div>
              </div>

              <button class="btn btn-sm btn-outline text-xs py-1 px-3 shrink-0">View</button>
            </div>
          </div>
        </div>

        <div v-else class="card flex-1 flex flex-col p-0 overflow-hidden min-h-0">
          <div class="p-2 border-b border-color bg-surface flex justify-between items-center shrink-0">
            <div class="flex items-center gap-2 min-w-0">
              <button class="btn btn-sm btn-outline text-muted text-xs" @click="selectedDoc = null">
                ← Library
              </button>
              <h2 class="pdf-title truncate">{{ selectedDoc.title }}</h2>
            </div>
          </div>
          <iframe :src="pdfUrl" class="w-full flex-1 bg-background" frameborder="0"></iframe>
        </div>
      </div>

      <!-- RIGHT: CHAT -->
      <div class="w-1/2 card p-0 flex flex-col border-primary shadow-sm chat-shell min-h-0">
        <div class="chat-header">
          <div class="chat-header-left">
            <h2 class="chat-title">SOP Chabot</h2>
          </div>
        </div>

        <div class="chat-body flex flex-col flex-1 min-h-0">
          <div id="chat-container" class="chat-messages">
            <div class="chat-intro">
              
            </div>

            <div
              v-for="(msg, idx) in chatMessages"
              :key="idx"
              class="chat-bubble text-sm whitespace-pre-line shadow-sm"
              :class="msg.role === 'user' ? 'user-bubble self-end' : 'bot-bubble self-start'"
              v-html="formatMarkdown(msg.text)"
            ></div>

            <div v-if="isTyping" class="chat-bubble bot-bubble self-start text-sm text-muted">
              <span class="typing-indicator">Retreiving from doc...</span>
            </div>
          </div>

          <form @submit.prevent="sendMessage" class="chat-input-bar">
            <input
              type="text"
              v-model="chatInput"
              class="form-control m-0 flex-1 text-sm"
              placeholder="Ask a question..."
              required
              :disabled="isTyping"
            />
            <button type="submit" class="btn btn-primary px-4 shrink-0" :disabled="isTyping">
              Ask
            </button>
          </form>
        </div>
      </div>
    </div>

    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal-content card">
        <h2 class="text-xl mb-4">Upload New SOP</h2>
        <form @submit.prevent="uploadSOP" class="flex flex-col gap-4">
          <div>
            <label class="text-xs font-bold">Document Title *</label>
            <input type="text" v-model="uploadForm.title" required class="form-control" />
          </div>

          <div>
            <label class="text-xs font-bold">Category</label>
            <select v-model="uploadForm.category" class="form-control">
              <option>General</option>
              <option>Emergency</option>
              <option>Pharmacy</option>
              <option>Admin & Compliance</option>
            </select>
          </div>

          <div>
            <label class="text-xs font-bold">PDF File *</label>
            <input
              type="file"
              @change="handleFileChange"
              accept="application/pdf"
              required
              class="form-control p-2"
            />
          </div>

          <div class="flex gap-4 mt-4">
            <button type="submit" class="btn btn-primary flex-1" :disabled="isUploading">
              {{ isUploading ? 'Uploading...' : 'Upload' }}
            </button>
            <button type="button" class="btn btn-outline flex-1" @click="showUploadModal = false">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import api from '../../services/api'

// --- STATE ---
const docs = ref([])
const isLoadingDocs = ref(false)
const searchQuery = ref('')
const selectedDoc = ref(null)

const showUploadModal = ref(false)
const isUploading = ref(false)
const uploadForm = ref({ title: '', category: 'General', file: null })

const chatMessages = ref([])
const chatInput = ref('')
const isTyping = ref(false)

// --- HELPERS ---
const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString('en-GB')
const pdfUrl = computed(() =>
  selectedDoc.value
    ? `http://127.0.0.1:5000/sops/${selectedDoc.value.id}/view#toolbar=0&navpanes=0&scrollbar=1&zoom=page-width`
    : ''
)

const filteredDocs = computed(() => {
  if (!searchQuery.value) return docs.value
  return docs.value.filter((d) =>
    d.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

// lightweight markdown
const formatMarkdown = (text) => {
  if (!text) return ''
  let safeText = text.replace(/</g, '&lt;').replace(/>/g, '&gt;')
  safeText = safeText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  return safeText
}

// --- API FETCH ---
const fetchDocs = async () => {
  isLoadingDocs.value = true
  try {
    const res = await api.get('/sops')
    docs.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    isLoadingDocs.value = false
  }
}

onMounted(fetchDocs)

const selectDocument = (doc) => {
  selectedDoc.value = doc
}

const handleFileChange = (e) => {
  uploadForm.value.file = e.target.files[0]
}

const uploadSOP = async () => {
  if (!uploadForm.value.file) return

  isUploading.value = true
  const formData = new FormData()
  formData.append('file', uploadForm.value.file)
  formData.append('title', uploadForm.value.title)
  formData.append('category', uploadForm.value.category)

  try {
    await api.post('/sops/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    showUploadModal.value = false
    uploadForm.value = { title: '', category: 'General', file: null }
    fetchDocs()
  } catch (err) {
    alert('Upload failed')
  } finally {
    isUploading.value = false
  }
}

// --- CHAT ---
const scrollToBottom = () => {
  nextTick(() => {
    const container = document.getElementById('chat-container')
    if (container) container.scrollTop = container.scrollHeight
  })
}

const sendMessage = async () => {
  if (!chatInput.value.trim()) return

  const userText = chatInput.value
  chatMessages.value.push({ role: 'user', text: userText })
  chatInput.value = ''
  isTyping.value = true
  scrollToBottom()

  try {
    const res = await api.post('/sops/chat', { message: userText })
    chatMessages.value.push({ role: 'bot', text: res.data.answer })
  } catch (err) {
    
    const errorMessage = err.response?.data?.error || 'Sorry, I encountered an error searching the knowledge base.'
    
    chatMessages.value.push({
      role: 'bot',
      text: errorMessage
    })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
/* Core */
.h-full { height: 100%; }
.flex-1 { flex: 1; }
.overflow-hidden { overflow: hidden; }
.overflow-y-auto { overflow-y: auto; }
.w-1\/2 { width: 50%; }
.sticky { position: sticky; }
.top-0 { top: 0; }
.self-end { align-self: flex-end; }
.self-start { align-self: flex-start; }
.truncate { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.min-h-0 { min-height: 0; }
.shrink-0 { flex-shrink: 0; }

/* Main layout */
.main-grid {
  height: calc(100vh - 180px);
  min-height: 0;
}
/* Library */
.library-card {
  border-radius: 18px;
}

.library-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.library-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.library-search {
  width: 220px;
  max-width: 220px;
  font-size: 0.85rem;
}

.doc-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 10px;
  padding: 0.9rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.18s ease;
  background: var(--surface);
}

.doc-item:hover {
  border-color: var(--primary);
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
  transform: translateY(-1px);
}

.doc-icon-wrap {
  padding: 0.65rem;
  background-color: var(--primary-light);
  color: var(--primary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.doc-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-main);
  margin: 0 0 0.2rem 0;
  line-height: 1.25;
}

.doc-meta {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0;
}

/* Chat shell */
.chat-shell {
  height: 580px;
  border-width: 1px;
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chat-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  border-bottom: 0px solid var(--border-color);
}

.chat-messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1rem;
  border-radius: 30px;
  background: linear-gradient(to bottom, rgba(248, 250, 252, 0.95), rgba(248, 250, 252, 1));
}

.chat-intro {
  text-align: center;
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-bottom: 0.35rem;
  padding: 0.25rem 1rem 0.5rem;
  line-height: 1.5;
}

/* Chat bubbles */
.chat-bubble {
  max-width: 82%;
  padding: 0.6rem 0.9rem;
  line-height: 1.6;
  border-radius: 16px;
  word-break: break-word;
}

.user-bubble {
  background-color: var(--primary);
  color: #ffffff;
  border-bottom-right-radius: 4px;
}

.bot-bubble {
  background-color: #f8fafc;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 4px;
}

.chat-input-bar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.9rem 1rem;
  border-top: none;
  background: var(--surface);
}

/* Markdown strong */
:deep(strong) {
  font-weight: 700;
  color: inherit;
}

.whitespace-pre-line {
  white-space: pre-line;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 50;
}

.modal-content {
  width: 100%;
  max-width: 500px;
  background-color: var(--surface);
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

/* Theme helpers */
.border-color { border-color: var(--border-color); }
.bg-surface { background-color: var(--surface); }
.bg-background { background-color: var(--background); }
.bg-primary-light { background-color: var(--primary-light); }
.text-main { color: var(--text-main); }
.text-muted { color: var(--text-muted); }

.form-control {
  width: 100%;
  padding: 0.7rem 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background-color: var(--background);
  color: var(--text-main);
  margin-top: 0.25rem;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.pdf-title {
  font-size: 1.25rem;
  font-weight: 500;
  color: var(--text-main);
  line-height: 1.2;
  margin: 15px;
}
</style>