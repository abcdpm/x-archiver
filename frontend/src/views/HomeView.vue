<script setup>
import { ref, onMounted } from 'vue'
import { getTweets, startSync } from '../api/index'
import TweetCard from '../components/TweetCard.vue'

const tweets = ref([])
const page = ref(1)
const total = ref(0)
const loading = ref(false)
const syncing = ref(false)

const loadTweets = async () => {
  if (loading.value) return
  loading.value = true
  try {
    const data = await getTweets(page.value, 20)
    tweets.value.push(...data.data)
    total.value = data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSync = async () => {
  syncing.value = true
  try {
    await startSync('elonmusk') // 可改为从输入框获取
    alert('后台同步任务已启动')
  } catch (error) {
    alert('同步触发失败')
  } finally {
    syncing.value = false
  }
}

const loadMore = () => {
  page.value++
  loadTweets()
}

onMounted(() => {
  loadTweets()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-800 font-sans pb-10">
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold">X Archiver</h1>
        <button 
          @click="handleSync" 
          :disabled="syncing"
          class="bg-black text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-gray-800 disabled:opacity-50 cursor-pointer">
          {{ syncing ? '任务发送中...' : '开始同步抓取' }}
        </button>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 mt-6">
      <div class="columns-1 sm:columns-2 lg:columns-3 gap-6">
        <TweetCard v-for="tweet in tweets" :key="tweet.tweet_id" :tweet="tweet" />
      </div>
      
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