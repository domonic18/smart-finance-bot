<template>
  <div id="app">
    <h1>流式对话应用</h1>
    <ChatComponent ></ChatComponent>
  </div>
</template>

<script>
import ChatComponent from "@/components/ChatComponent.vue";

export default {
  name: 'App',
  components: {
    ChatComponent
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
