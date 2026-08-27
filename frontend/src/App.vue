<script setup>
import { ref, onMounted } from 'vue'

const tweets = ref([])
const page = ref(1)
const total = ref(0)
const loading = ref(false)
const syncing = ref(false)

// 获取推文列表
const fetchTweets = async () => {
  if (loading.value) return
  loading.value = true
  try {
    const res = await fetch(`/api/tweets?page=${page.value}&size=20`)
    const json = await res.json()
    tweets.value.push(...json.data)
    total.value = json.total
  } catch (error) {
    console.error('获取推文失败:', error)
  } finally {
    loading.value = false
  }
}

// 触发后台同步
const handleSync = async () => {
  syncing.value = true
  try {
    await fetch('/api/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'elonmusk' }) // 替换为你需要抓取的账号
    })
    alert('抓取和下载任务已在后台启动！')
  } catch (error) {
    alert('触发同步失败')
  } finally {
    syncing.value = false
  }
}

const loadMore = () => {
  page.value++
  fetchTweets()
}

// 判断使用本地图片还是网络原图
const getMediaUrl = (media) => {
  return media.download_status === 1 && media.local_path
    ? `/media/${media.local_path}`
    : media.original_url
}

onMounted(() => {
  fetchTweets()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-800 font-sans pb-10">
    <!-- 顶部导航 -->
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold flex items-center gap-2">
          <svg class="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          X Archiver
        </h1>
        <button 
          @click="handleSync" 
          :disabled="syncing"
          class="bg-black text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-gray-800 disabled:opacity-50 transition-colors cursor-pointer">
          {{ syncing ? '任务发送中...' : '开始同步抓取' }}
        </button>
      </div>
    </header>

    <!-- 瀑布流容器 -->
    <main class="max-w-7xl mx-auto px-4 mt-6">
      <div class="columns-1 sm:columns-2 lg:columns-3 gap-6">
        
        <!-- 卡片组件 -->
        <div 
          v-for="tweet in tweets" 
          :key="tweet.tweet_id"
          class="break-inside-avoid mb-6 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow"
        >
          <div class="p-4">
            <!-- 作者信息 -->
            <div class="flex items-center gap-3 mb-3">
              <img :src="tweet.author_avatar" class="w-10 h-10 rounded-full bg-gray-200" alt="avatar" />
              <div>
                <p class="font-bold text-sm leading-tight">{{ tweet.author_name }}</p>
                <p class="text-gray-500 text-xs">@{{ tweet.author_handle }} · {{ new Date(tweet.posted_at).toLocaleDateString() }}</p>
              </div>
            </div>
            
            <!-- 推文文本 -->
            <p class="text-sm text-gray-800 whitespace-pre-wrap mb-3 leading-relaxed">{{ tweet.content }}</p>
          </div>

          <!-- 媒体网格 -->
          <div v-if="tweet.media && tweet.media.length > 0" class="border-t border-gray-50">
            <div :class="tweet.media.length > 1 ? 'grid grid-cols-2 gap-1 p-1' : ''">
              <div v-for="m in tweet.media" :key="m.id" class="relative group">
                
                <!-- 视频渲染 -->
                <video 
                  v-if="m.media_type === 'video'" 
                  :src="getMediaUrl(m)" 
                  controls 
                  class="w-full object-cover"
                  :class="tweet.media.length > 1 ? 'aspect-square' : ''"
                ></video>
                
                <!-- 图片渲染 -->
                <img 
                  v-else 
                  :src="getMediaUrl(m)" 
                  class="w-full object-cover cursor-zoom-in"
                  :class="tweet.media.length > 1 ? 'aspect-square' : ''"
                  loading="lazy"
                />
                
                <!-- 下载状态指示器 -->
                <div v-if="m.download_status !== 1" class="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded-md backdrop-blur-sm">
                  {{ m.download_status === 0 ? '云端原图' : '下载失败' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载更多逻辑 -->
      <div class="py-10 text-center">
        <button 
          v-if="tweets.length < total" 
          @click="loadMore"
          :disabled="loading"
          class="bg-gray-100 text-gray-700 px-6 py-2 rounded-full text-sm font-medium hover:bg-gray-200 disabled:opacity-50 cursor-pointer">
          {{ loading ? '加载中...' : '加载更多' }}
        </button>
        <p v-else-if="tweets.length > 0" class="text-gray-400 text-sm">已经到底啦</p>
      </div>
    </main>
  </div>
</template>