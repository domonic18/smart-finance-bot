<template>
  <div class="chat-container">
    <div class="messages">
      <div v-for="(message, index) in messages" :key="index" class="message">
        <strong>{{ message.sender }}:</strong> {{ message.text }}
      </div>
    </div>
    <input v-model="userInput" @keyup.enter="sendMessage" placeholder="输入消息..." />
  </div>
</template>

<script>
export default {
  data() {
    return {
      messages: [],
      userInput: '',
    };
  },
  methods: {
    sendMessage() {
      if (this.userInput.trim() === '') return;

      // 添加用户消息
      this.messages.push({ sender: '我', text: this.userInput });

      // 发送消息到后端（假设后端有一个 API 接口）
      this.fetchResponse(this.userInput);
      this.userInput = ''; // 清空输入框
    },
    async fetchResponse(message) {
      // 构建请求数据
      const data = {
        ad_words: message, // 从编辑框获取
      };

      // 后端接口为 /gen
      try {
        const response = await fetch('http://localhost:8082/gen/invoke', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ input: data }),
        });
        const dataResponse = await response.json(); // 修改为 dataResponse
        // 添加后端返回的消息
        this.messages.push({ sender: '机器人', text: dataResponse.output });
      } catch (error) {
        console.error('Error:', error);
      }
    },
  },
};
</script>

<style>
.chat-container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
}
.messages {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 10px;
}
.message {
  margin: 5px 0;
}
input {
  width: 100%;
  padding: 10px;
}
</style>
