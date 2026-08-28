<script setup>
defineProps({
  tweet: {
    type: Object,
    required: true
  }
})

const getMediaUrl = (media) => {
  return media.download_status === 1 && media.local_path
    ? `/media/${media.local_path}`
    : media.original_url
}
</script>

<template>
  <div class="break-inside-avoid mb-6 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow">
    <div class="p-4">
      <div class="flex items-center gap-3 mb-3">
        <img :src="tweet.author_avatar" class="w-10 h-10 rounded-full bg-gray-200" alt="avatar" />
        <div>
          <p class="font-bold text-sm leading-tight">{{ tweet.author_name }}</p>
          <p class="text-gray-500 text-xs">@{{ tweet.author_handle }} · {{ new Date(tweet.posted_at).toLocaleDateString() }}</p>
        </div>
      </div>
      <p class="text-sm text-gray-800 whitespace-pre-wrap mb-3 leading-relaxed">{{ tweet.content }}</p>
    </div>

    <div v-if="tweet.media && tweet.media.length > 0" class="border-t border-gray-50">
      <div :class="tweet.media.length > 1 ? 'grid grid-cols-2 gap-1 p-1' : ''">
        <div v-for="m in tweet.media" :key="m.id" class="relative group">
          <video 
            v-if="m.media_type === 'video'" 
            :src="getMediaUrl(m)" 
            controls 
            class="w-full object-cover"
            :class="tweet.media.length > 1 ? 'aspect-square' : ''"
          ></video>
          <img 
            v-else 
            :src="getMediaUrl(m)" 
            class="w-full object-cover cursor-zoom-in"
            :class="tweet.media.length > 1 ? 'aspect-square' : ''"
            loading="lazy"
          />
          <div v-if="m.download_status !== 1" class="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded-md backdrop-blur-sm">
            {{ m.download_status === 0 ? '云端原图' : '下载失败' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>