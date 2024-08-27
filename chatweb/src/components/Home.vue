<template>
  <main class="main-container">
    <div class="text-center">
      <h1 class="main-title">金融千问机器人演示页面</h1>
      <p class="project-description">
        这是一个基于Agent+RAG实现的金融千问机器人，前端使用vue.js，后端通过langchain+agent+chroma实现对金融数据的向量化存储，最终前端和后端通过流式api进行数据交互。
      </p>
      <div class="button-container">
        <router-link to="/chat/" class="start-button">快速开始</router-link>
      </div>
    </div>
  </main>
</template>

<style scoped>
.main-container {
  display: grid;
  min-height: 100vh;
  place-items: center;
  background-color: white;
  padding: 6rem 1.5rem; /* px-6 py-24 */
}

.main-title {
  margin-top: 1rem;
  font-size: 2rem; /* text-3xl */
  font-weight: bold;
  color: #1f2937; /* text-gray-900 */
  text-align: center;
}

.project-description {
  margin-top: 1.5rem;
  font-size: 1rem; /* text-base */
  line-height: 1.75; /* leading-7 */
  color: #4b5563; /* text-gray-600 */
}

.button-container {
  margin-top: 2.5rem;
  display: flex;
  justify-content: center;
  gap: 1.5rem; /* gap-x-6 */
}

.start-button {
  border-radius: 0.375rem; /* rounded-md */
  background-color: #4f46e5; /* bg-indigo-600 */
  padding: 0.625rem 0.875rem; /* px-3.5 py-2.5 */
  font-size: 1.125rem; /* text-lg */
  font-weight: 600; /* font-semibold */
  color: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  transition: background-color 0.2s;
}

.start-button:hover {
  background-color: #4338ca; /* hover:bg-indigo-500 */
}

.start-button:focus-visible {
  outline: 2px solid #6366f1; /* focus-visible:outline-indigo-600 */
  outline-offset: 2px; /* focus-visible:outline-offset-2 */
}
</style>
